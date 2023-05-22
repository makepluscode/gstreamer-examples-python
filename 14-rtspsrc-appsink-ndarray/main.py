import os
import config

from gi.repository import Gst, GLib
import sys
import gi
from datetime import datetime

import numpy as np

gi.require_version('Gst', '1.0')

# gst pipeline
# gst-launch-1.0 rtspsrc location='rtsp://makepluscode:000000@192.168.219.155/stream1' ! rtph264depay ! h264parse ! decodebin ! autovideosink


def graph_pipeline(pipeline):
    Gst.debug_bin_to_dot_file(pipeline, Gst.DebugGraphDetails.ALL,
                              "pipeline")
    try:
        os.system("dot -Tpng -o ./pipeline.png ./pipeline.dot")
    except Exception as e:
        print(e)


def on_message(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
    msg = message.type
    # print("on_message : " + msg)
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


def covert_buffer_to_nparray(buffer):
    if buffer:
        arr = np.ndarray(
            (1920,
             1080,
             3),
            buffer=buffer.extract_dup(0, buffer.get_size()),
            dtype=np.uint8)
    else:
        arr = None
    return arr


nparray_old = None


now_old = datetime.now()

def on_buffer(sink, data):

    now = datetime.now()
    global now_old

    global cnt
    global nparray_old

    sample = sink.emit("pull-sample")

    caps = sample.get_caps()

    buffer = sample.get_buffer()
    height = caps.get_structure(0).get_value("height")
    width = caps.get_structure(0).get_value("width")

    nparray_new = covert_buffer_to_nparray(buffer)

    if np.array_equal(nparray_new, nparray_old):
        print(now.strftime('%Y-%m-%d %H:%M:%S'), "%06d" % now.microsecond, "%s " % (now-now_old), "array is same!")        
        # sample = sink.emit("pull-sample")
        return True
    else:
        print(now.strftime('%Y-%m-%d %H:%M:%S'), "%06d" % now.microsecond, "%s " % (now-now_old), "array is different!")

    buffer_old = Gst.Buffer()
    buffer_old = buffer.copy_deep()
    nparray_old = covert_buffer_to_nparray(buffer_old)

    now_old = now
    return True


def create_pipepline(pipeline: Gst.Pipeline):
    src = Gst.ElementFactory.make("rtspsrc", "src")
    src.set_property(
        "location", "rtsp://" + config.USERNAME + ":" + config.PASSWORD + "@" + config.IPADDRESS + "/stream1")
    src.set_property("latency", 1000)
    src.set_property("drop-on-latency", False)
    src.set_property("udp-buffer-size", 20971520)
    src.set_property("do-rtsp-keep-alive", 1)

    queue = Gst.ElementFactory.make("queue", "queue")
    queue.set_property("max-size-buffers", 16)
    depay = Gst.ElementFactory.make("rtph264depay", "depay")
    parse = Gst.ElementFactory.make("h264parse", "parse")
    decode = Gst.ElementFactory.make("avdec_h264", "decode")
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    videorate = Gst.ElementFactory.make("videorate", "videorate")
    capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
    caps = Gst.Caps.from_string("video/x-raw, format=RGB")
    sink = Gst.ElementFactory.make("appsink", "sink")
    sink.set_property("emit-signals", True)
    sink.set_property("max-buffers", 32)
    sink.set_property("drop", False)
    sink.set_property("sync", False)

    if (not src or not depay or not parse or not decode or not convert or not sink):
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    pipeline.add(src)
    pipeline.add(queue)
    pipeline.add(depay)
    pipeline.add(parse)
    pipeline.add(decode)
    pipeline.add(convert)
    pipeline.add(capsfilter)
    pipeline.add(sink)

    def on_rtspsrc_pad_added(rtspsrc, pad, depay):
        string = pad.query_caps(None).to_string()
        print(pad.name)
        print(string)
        src.link(queue)
        queue.link(depay)

    src.connect("pad-added", on_rtspsrc_pad_added, depay)

    ret = depay.link(parse)
    ret = ret and parse.link(decode)
    ret = ret and decode.link(convert)
    #ret = ret and convert.link(sink)
    ret = ret and convert.link(capsfilter)
    ret = ret and capsfilter.link_filtered(sink, caps)

    if not ret:
        print("ERROR: Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: Elements could be linked")

    sink.connect("new-sample", on_buffer, sink)
    return True


def main():
    Gst.init(sys.argv)

    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(3)

    # create a pipeline with factory
    pipeline = Gst.Pipeline()

    create_pipepline(pipeline)

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
