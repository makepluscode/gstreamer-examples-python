import numpy as np
import os

from gi.repository import Gst, GObject, GLib

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

    elif msg == Gst.MessageType.INFO:
        err, debug = message.parse_info()
        print("on_message : Info -", err, debug)

    return True


def start_feed(src, length):
    ndarray = np.full((640, 480, 3), 0, dtype=np.uint8)
    buffer = Gst.Buffer.new_wrapped(ndarray.tobytes())
    gst_flow_return = src.emit("push-buffer",  buffer)

    if gst_flow_return != Gst.FlowReturn.OK:
        print('error')


def stop_feed():
    print("stop feed")


def create_pipepline(pipeline: Gst.Pipeline):
    src = Gst.ElementFactory.make("appsrc", "src")

    caps = Gst.Caps.from_string(
        "video/x-raw,format=RGB,width=640,height=480,framerate=30/1")
    src.set_property("format", Gst.Format.TIME)
    src.set_property('is-live', True)
    src.set_property('do-timestamp', True)
    src.set_property('caps', caps)
    src.connect('need-data', start_feed)
    src.connect('enough-data', stop_feed)

    queue = Gst.ElementFactory.make("queue", "queue")

    convert = Gst.ElementFactory.make("videoconvert", "convert")

    overlay = Gst.ElementFactory.make("clockoverlay", "overlay")
    overlay.set_property('time-format', "%D %H:%M:%S:%L")

    encode = Gst.ElementFactory.make("jpegenc", "encode")
    encode.set_property('quality', 85)

    sink = Gst.ElementFactory.make("multifilesink", "sink")
    sink.set_property('location', "captured%08d.jpg")

    if (not src or not queue or not overlay or not convert or not sink):
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    pipeline.add(src)
    pipeline.add(queue)
    pipeline.add(convert)
    pipeline.add(overlay)
    pipeline.add(encode)
    pipeline.add(sink)

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


def main():
    Gst.init(sys.argv)

    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(3)

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
