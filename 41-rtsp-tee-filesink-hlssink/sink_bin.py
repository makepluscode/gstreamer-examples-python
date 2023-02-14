from gi.repository import Gst, GLib, GObject
import debugpy

import os
import config
import sys
import gi
import numpy as np

import time

import fsutil

from common import sample_queue, SampleWapper
from pipeline import PipelineClass


np_framebuffer = np.full((1920, 1080, 3), 0, dtype=np.uint8)

"""
gst-launch-1.0 testvideosrc num-buffers=300 ! videoconvert ! tee name=t ! \
    queue ! avenc_h264_omx ! h264parse ! mp4mux ! hlssink max-files=5 t. ! \
    queue ! autovideosink
"""


def create_sink_bin():
    bin = Gst.Bin.new("filesink-bin")
    if not bin:
        print("ERROR: Unable to create bin")

    """ 1st bin : appsrc to tee """
    appsrc = Gst.ElementFactory.make("appsrc", "appsrc")
    caps = Gst.Caps.from_string(
        "video/x-raw, format=RGB, width=1920, height=1080, framerate=10/1")
    appsrc.set_property("format", Gst.Format.TIME)
    appsrc.set_property("is-live", True)
    appsrc.set_property("do-timestamp", True)
    appsrc.set_property("caps", caps)
    appsrc.connect("need-data", start_feed)
    appsrc.connect("enough-data", stop_feed)

    convert = Gst.ElementFactory.make("videoconvert", "convert")

    overlay = Gst.ElementFactory.make("clockoverlay", "overlay")
    overlay.set_property("time-format", "%D %H:%M:%S")
    overlay.set_property("halignment", "center")
    overlay.set_property("valignment", "center")
    overlay.set_property("text", "####")
    overlay.set_property("shaded-background", "true")
    overlay.set_property("font-desc", "Sans, 32")

    jpeg_encode = Gst.ElementFactory.make("jpegenc", "jpeg_encode")
    jpeg_encode.set_property("quality", 80)

    tee = Gst.ElementFactory.make("tee", "tee")

    if not appsrc or not convert or not overlay or not jpeg_encode or not tee:
        print("ERROR: 1st elements could be not created.")
        sys.exit(1)

    Gst.Bin.add(bin, appsrc)
    Gst.Bin.add(bin, convert)
    Gst.Bin.add(bin, overlay)
    Gst.Bin.add(bin, jpeg_encode)
    Gst.Bin.add(bin, tee)

    ret = appsrc.link(convert)
    ret = ret and convert.link(overlay)
    ret = ret and overlay.link(jpeg_encode)
    ret = ret and jpeg_encode.link(tee)

    if not ret:
        print("ERROR: 1st Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: 1st Elements could be linked")

    """ 2nd bin : multi jpeg files """
    file_queue = Gst.ElementFactory.make("queue", "file_queue")

    filesink = Gst.ElementFactory.make("multifilesink", "filesink")
    filesink.set_property("location", "dummy.jpg")
    filesink.set_property("post-messages", True)

    if not file_queue or not filesink:
        print("ERROR: 2nd elements could be not created.")
        sys.exit(1)

    Gst.Bin.add(bin, file_queue)
    Gst.Bin.add(bin, filesink)

    ret = ret and tee.link(file_queue)
    ret = ret and file_queue.link(filesink)

    if not ret:
        print("ERROR: 2nd Elements could not be linked ")
        sys.exit(1)
    else:
        print("DONE: 2nd Elements could be linked")

    """ 3nd bin : the latest jpeg files """
    hls_queue = Gst.ElementFactory.make("queue", "hls_queue")
    fakesink = Gst.ElementFactory.make("fakesink", "fakesink")

    if not hls_queue or not fakesink:
        print("ERROR: elements could be not created. 3rd")
        sys.exit(1)

    Gst.Bin.add(bin, hls_queue)
    Gst.Bin.add(bin, fakesink)

    ret = ret and tee.link(hls_queue)
    ret = ret and hls_queue.link(fakesink)

    if not ret:
        print("ERROR: 3rd Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: 3rd Elements could be linked")

    return bin


def start_feed(src, length):
    # debugpy.debug_this_thread()

    global np_framebuffer
    queue_size = sample_queue.qsize()
    if queue_size < 1:
        time.sleep(1)
        fsutil.print_statistics()
        print("sample_queue is empty")
    else:
        time.sleep(0.01)

        samplebox = sample_queue.get()

        sample = samplebox.sample
        camera = samplebox.camera
        caps = sample.get_caps()

        # get meta data from gst sample
        height = caps.get_structure(0).get_value("height")
        width = caps.get_structure(0).get_value("width")

        # get buffer from sample
        buffer = sample.get_buffer()
        print("(%d)" % camera, buffer.pts, buffer.dts,
              buffer.offset, ", size ", height, width)

        path = fsutil.get_path()
        pipeline = PipelineClass.instance()

        # set file name and text to distinguish each cameras
        sink_element = pipeline.get_element("filesink")
        sink_element.set_property("location", path + "/ch%02d" %
                                  camera + "_%04d.jpg" % buffer.offset)
        overlay_element = pipeline.get_element("overlay")
        overlay_element.set_property(
            "text", "Camera%d - %4d\n" % (camera, buffer.offset))

        success, map_info = buffer.map(Gst.MapFlags.READ)

        if not success:
            raise RuntimeError("fail to map")

        # update framebuffer
        np_framebuffer = np.ndarray(
            shape=(width, height, 3), dtype=np.uint8, buffer=map_info.data
        )

        buffer.unmap(map_info)

    gst_buffer = Gst.Buffer.new_wrapped(np_framebuffer.tobytes())
    gst_flow_return = src.emit("push-buffer", gst_buffer)

    if gst_flow_return != Gst.FlowReturn.OK:
        raise RuntimeError("fail to feed")

    return True


def stop_feed():
    print("stop feed")
    return True
