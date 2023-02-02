
from gi.repository import Gst, GLib
import sys
import gi

gi.require_version('Gst', '1.0')

# gst pipeline
# gst-launch-1.0 filesrc location=../video/road.mp4 ! qtdemux ! h264parse ! avdec_h264 ! videoconvert ! videovideorate ! video/x-raw,framevideorate=10/1 ! autovideosink


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

    return True


def create_pipepline(pipeline: Gst.Pipeline):
    src = Gst.ElementFactory.make("filesrc", "src")
    src.set_property("location", "../video/road.mp4")

    demux = Gst.ElementFactory.make("qtdemux", "demux")
    parse = Gst.ElementFactory.make("h264parse", "parse")
    decode = Gst.ElementFactory.make("avdec_h264", "decode")
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    videorate = Gst.ElementFactory.make("videorate", "videorate")
    caps = Gst.Caps.from_string("video/x-raw, framerate=10/1")
    sink = Gst.ElementFactory.make("autovideosink", "sink")

    if (not src or not demux or not parse or not decode or not convert or not sink):
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    pipeline.add(src)
    pipeline.add(demux)
    pipeline.add(parse)
    pipeline.add(decode)
    pipeline.add(convert)
    pipeline.add(videorate)
    pipeline.add(sink)

    ret = src.link(demux)

    def demuxer_pad_added(demuxer, pad, parse):
        if pad.name == 'video_0':
            demuxer.link(parse)

    demux.connect("pad-added", demuxer_pad_added, parse)

    ret = ret and parse.link(decode)
    ret = ret and decode.link(convert)
    ret = ret and convert.link(videorate)
    ret = ret and videorate.link_filtered(sink, caps)

    if not ret:
        print("ERROR: Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: Elements could be linked")

    return True


def main():
    Gst.init(sys.argv)

    # create a pipeline with factory
    pipeline = Gst.Pipeline()

    create_pipepline(pipeline)

    pipeline.set_state(Gst.State.PLAYING)

    loop = GLib.MainLoop()

    # connect bus to catch signal from the pipeline
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    # run
    try:
        loop.run()
    except:
        pass

    # if fails, then clean
    pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    main()
