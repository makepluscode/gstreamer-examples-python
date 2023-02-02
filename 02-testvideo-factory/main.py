from gi.repository import Gst, GLib
import sys

import gi
gi.require_version('Gst', '1.0')


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
    src = Gst.ElementFactory.make("videotestsrc", "src")
    src.set_property("pattern", 18)
    src.set_property("num-buffers", 300)

    sink = Gst.ElementFactory.make("autovideosink", "sink")

    pipeline.add(src)
    pipeline.add(sink)

    src.link(sink)
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
    loop.run()

    # if fails, then clean
    pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    main()
