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


def create_sink_bin():
    bin = Gst.Bin.new("filesink-bin")
    if not bin:
        print("ERROR: Unable to create bin")

    appsrc = Gst.ElementFactory.make("appsrc", "appsrc")
    caps = Gst.Caps.from_string("video/x-raw, format=RGB, width=1920, height=1080, framerate=10/1")
    appsrc.set_property("format", Gst.Format.TIME)
    appsrc.set_property("is-live", True)
    appsrc.set_property("do-timestamp", True)
    appsrc.set_property("caps", caps)
    appsrc.connect("need-data", start_feed)
    appsrc.connect("enough-data", stop_feed)

    file_queue = Gst.ElementFactory.make("queue", "file_queue")

    convert = Gst.ElementFactory.make("videoconvert", "convert")

    overlay = Gst.ElementFactory.make("clockoverlay", "overlay")
    overlay.set_property("time-format", "%D %H:%M:%S")

    encode = Gst.ElementFactory.make("jpegenc", "encode")
    encode.set_property("quality", 85)

    sink = Gst.ElementFactory.make("multifilesink", "filesink")
    sink.set_property("location", "dummy.jpg")

    if not appsrc or not file_queue or not overlay or not convert or not sink:
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    Gst.Bin.add(bin, appsrc)
    Gst.Bin.add(bin, file_queue)
    Gst.Bin.add(bin, convert)
    Gst.Bin.add(bin, overlay)
    Gst.Bin.add(bin, encode)
    Gst.Bin.add(bin, sink)

    ret = appsrc.link(file_queue)
    ret = ret and file_queue.link(convert)
    ret = ret and convert.link(overlay)
    ret = ret and overlay.link(encode)
    ret = ret and encode.link(sink)

    if not ret:
        print("ERROR: Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: Elements could be linked")

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

        # set file name to distinguish each cameras
        path = fsutil.get_path()
        pipeline = PipelineClass.instance()

        sink_element = pipeline.get_element("filesink")
        sink_element.set_property("location", path + "/ch%02d" %
                                  camera + "_%04d.jpg" % buffer.offset)

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
