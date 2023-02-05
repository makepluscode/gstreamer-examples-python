import os
import config

from gi.repository import Gst, GLib
import sys
import gi

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


cnt = 0


def on_buffer(sink, data):
    global cnt
    sample = sink.emit("pull-sample")
    buffer = sample.get_buffer()
    print("on_buffer: frame count -", cnt)
    cnt = cnt + 1
    return True


def create_pipepline(pipeline: Gst.Pipeline):
    src = Gst.ElementFactory.make("rtspsrc", "src")
    src.set_property(
        "location", "rtsp://" + config.USERNAME + ":" + config.PASSWORD + "@" + config.IPADDRESS + "/stream1")
    src.set_property("latency", 0)
    src.set_property("drop-on-latency", True)
    src.set_property("udp-buffer-size", 2097152)
    src.set_property("do-rtsp-keep-alive", 1)

    queue = Gst.ElementFactory.make("queue", "queue")
    queue.set_property("max-size-buffers", 4)
    depay = Gst.ElementFactory.make("rtph264depay", "depay")
    parse = Gst.ElementFactory.make("h264parse", "parse")
    decode = Gst.ElementFactory.make("avdec_h264", "decode")
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    videorate = Gst.ElementFactory.make("videorate", "videorate")
    caps = Gst.Caps.from_string("video/x-raw, framerate=30/1")
#    sink = Gst.ElementFactory.make("autovideosink", "sink")
    sink = Gst.ElementFactory.make("appsink", "sink")
    sink.set_property("emit-signals", True)
    sink.set_property("max-buffers", 2)
    sink.set_property("drop", True)
#    sink.set_property("sync", False)

    if (not src or not depay or not parse or not decode or not convert or not sink):
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    pipeline.add(src)
    pipeline.add(queue)
    pipeline.add(depay)
    pipeline.add(parse)
    pipeline.add(decode)
    pipeline.add(convert)
    pipeline.add(videorate)
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
    ret = ret and convert.link(sink)
#    ret = ret and convert.link(videorate)
#    ret = ret and videorate.link_filtered(sink, caps)
#    ret = ret and videorate.link_filtered(sink, caps)

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
