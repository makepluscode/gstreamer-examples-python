import numpy as np
from gi.repository import Gst, GLib, GObject
import debugpy

import os
import config
import sys
import gi

import time
import queue

gi.require_version("Gst", "1.0")

# global variables
queue = queue.Queue()
pipeline = None
np_framebuffer = np.full((1920, 1080, 3), 0, dtype=np.uint8)


def graph_pipeline(pipeline):
    Gst.debug_bin_to_dot_file(pipeline, Gst.DebugGraphDetails.ALL, "pipeline")
    try:
        os.system("dot -Tpng -o ./pipeline.png ./pipeline.dot")
    except Exception as e:
        print(e)


def on_message(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
    msg = message.type

    if msg == Gst.MessageType.EOS:
        print("on_message : End Of Stream")
        loop.quit()

    elif msg == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print("on_message : Warnning -", err, debug)

    elif msg == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print("on_message : Error -", err, debug)
        loop.quit()

    elif msg == Gst.MessageType.INFO:
        err, debug = message.parse_info()
        print("on_message : Info -", err, debug)

    return True


class SampleWapper:
    camera = -1
    sample = None

    def __init__(self, sample, camera) -> None:
        self.sample = sample
        self.camera = camera


def on_sample_camera_ch1(sink, data):
    # debugpy.debug_this_thread()

    gst_sample = sink.emit("pull-sample")
    sample = SampleWapper(gst_sample, 1)
    queue.put(sample)

    return True


def on_on_sample_camera_ch2(sink, data):
    # debugpy.debug_this_thread()

    gst_sample = sink.emit("pull-sample")
    sample = SampleWapper(gst_sample, 2)
    queue.put(sample)

    return True


""" 
gst-launch-1.0 rtspsrc location='rtsp://192.168.219.155/stream1' ! \
  rtph264depay ! h264parse ! decodebin ! videoconvert ! autovideosink
"""


def create_rtspsrc_bin(index, callback, uri):
    name = "rtspsrc-bin-%02d" % index
    bin = Gst.Bin.new(name)

    if not bin:
        print("ERROR: Unable to create bin")

    src = Gst.ElementFactory.make("rtspsrc", "src")

    src.set_property("location", uri)
    src.set_property("latency", 0)
    src.set_property("drop-on-latency", True)
    # src.set_property("udp-buffer-size", 2097152)
    # src.set_property("do-rtsp-keep-alive", 1)

    queue = Gst.ElementFactory.make("queue", "queue")
    queue.set_property("max-size-buffers", 4)
    depay = Gst.ElementFactory.make("rtph264depay", "depay")
    parse = Gst.ElementFactory.make("h264parse", "parse")
    decode = Gst.ElementFactory.make("avdec_h264", "decode")
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    videorate = Gst.ElementFactory.make("videorate", "videorate")
    caps = Gst.Caps.from_string("video/x-raw, framerate=1/1, format=RGB")

    sink = Gst.ElementFactory.make("appsink", "rtspsink-%d" % index)
    sink.set_property("emit-signals", True)
    sink.set_property("max-buffers", 4)
    sink.set_property("drop", False)
    sink.set_property("sync", False)

    if not src or not depay or not parse or not decode or not convert or not sink:
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    Gst.Bin.add(bin, src)
    Gst.Bin.add(bin, queue)
    Gst.Bin.add(bin, depay)
    Gst.Bin.add(bin, parse)
    Gst.Bin.add(bin, decode)
    Gst.Bin.add(bin, convert)
    Gst.Bin.add(bin, videorate)
    Gst.Bin.add(bin, sink)

    def on_rtspsrc_pad_added(rtspsrc, pad, depay):
        string = pad.query_caps(None).to_string()
        print(pad.name)
        src.link(queue)
        queue.link(depay)

    src.connect("pad-added", on_rtspsrc_pad_added, depay)

    ret = depay.link(parse)
    ret = ret and parse.link(decode)
    ret = ret and decode.link(convert)
    ret = ret and convert.link(videorate)
    ret = ret and videorate.link_filtered(sink, caps)

    if not ret:
        print("ERROR: Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: Elements could be linked")

    sink.connect("new-sample", callback, sink)

    return bin


def start_feed(src, length):
    # debugpy.debug_this_thread()

    global np_framebuffer

    queue_size = queue.qsize()
    if queue_size < 1:
        time.sleep(1)
        print("queue is empty")
    else:
        time.sleep(0.01)

        samplebox = queue.get()

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
        sink_element = pipeline.get_by_name("filesink")
        sink_element.set_property("location", "ch%02d" %
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
        print("error in feeding")

    return True


def stop_feed():
    print("stop feed")
    return True


def create_filesink_bin():
    bin = Gst.Bin.new("filesink-bin")
    if not bin:
        print("ERROR: Unable to create bin")

    src = Gst.ElementFactory.make("appsrc", "appsrc")

    caps = Gst.Caps.from_string("video/x-raw, format=RGB, width=1920, height=1080, framerate=10/1")
    src.set_property("format", Gst.Format.TIME)
    src.set_property("is-live", True)
    src.set_property("do-timestamp", True)
    src.set_property("caps", caps)
    src.connect("need-data", start_feed)
    src.connect("enough-data", stop_feed)

    queue = Gst.ElementFactory.make("queue", "queue")

    convert = Gst.ElementFactory.make("videoconvert", "convert")

    overlay = Gst.ElementFactory.make("clockoverlay", "overlay")
    overlay.set_property("time-format", "%D %H:%M:%S")

    encode = Gst.ElementFactory.make("jpegenc", "encode")
    encode.set_property("quality", 85)

    sink = Gst.ElementFactory.make("multifilesink", "filesink")
    sink.set_property("location", "chXX_%04d.jpg")

    if not src or not queue or not overlay or not convert or not sink:
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    Gst.Bin.add(bin, src)
    Gst.Bin.add(bin, queue)
    Gst.Bin.add(bin, convert)
    Gst.Bin.add(bin, overlay)
    Gst.Bin.add(bin, encode)
    Gst.Bin.add(bin, sink)

    ret = src.link(queue)
    ret = ret and queue.link(convert)
    ret = ret and convert.link(overlay)
    ret = ret and overlay.link(encode)
    ret = ret and encode.link(sink)

    if not ret:
        print("ERROR: Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: Elements could be linked")

    return bin


def main():
    Gst.init(sys.argv)

    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(3)

    # create a pipeline with factory
    global pipeline
    pipeline = Gst.Pipeline()

    # 1st bin : RTSP camera 1
    source_bin0 = create_rtspsrc_bin(
        0, on_sample_camera_ch1, "rtsp://" + config.USERNAME + ":" + config.PASSWORD + "@" + config.IPADDRESS + "/stream1")
    pipeline.add(source_bin0)

    # 2nd bin : RTSP camera 2
    source_bin1 = create_rtspsrc_bin(
        1, on_on_sample_camera_ch2, "rtsp://" + config.USERNAME + ":" + config.PASSWORD + "@" + config.IPADDRESS + "/stream1")
    pipeline.add(source_bin1)

    # 3nd bin : Jpeg encoding and filesink
    sink_bin = create_filesink_bin()
    pipeline.add(sink_bin)

    pipeline.set_state(Gst.State.PLAYING)

    loop = GLib.MainLoop()

    # connect bus to catch signal from the pipeline
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    graph_pipeline(pipeline)

    # run
    try:
        loop.run()
    except:
        pass

    # if fails, then clean
    pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    main()
