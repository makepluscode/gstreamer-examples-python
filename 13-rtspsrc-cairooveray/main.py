import os
import config

import cairo


from gi.repository import Gst, GLib
import sys
import gi

gi.require_version('Gst', '1.0')

# gst pipeline
# gst-launch-1.0 rtspsrc location='rtsp://makepluscode:000000@192.168.219.155/stream1' ! rtph264depay ! h264parse ! decodebin ! videoconvert ! autovideosink

OVERLAY_FRAME_WIDTH = 1920
OVERLAY_FRAME_HEIGHT = 1080


def graph_pipeline(pipeline):
    Gst.debug_bin_to_dot_file(pipeline, Gst.DebugGraphDetails.ALL,
                              "pipeline")
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


def on_draw(_overlay, context, _timestamp, _duration):
    # print("*_overlay = ", _overlay, "context = ",
    #      context, "*_timestamp = ", _timestamp)

    # creating shape
    context.rectangle(900, 500, 120, 80)

    # setting color of the context
    context.set_source_rgba(1.0, 0.0, 0.0, 0.5)

    # fill the color inside
    context.fill()

    # creating shape
    context.rectangle(1020, 500, 120, 80)

    # setting color of the context
    context.set_source_rgba(0.0, 1.0, 0.0, 1.0)

    # Setting outline width
    context.set_line_width(4)

    # stroke out the color and width property
    context.stroke()

    text = 'Hello, makepluscode'
    (x, y, w, h, dx, dy) = context.text_extents(text)
    context.select_font_face(
        'Open Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(40)
    context.set_source_rgba(0.0, 0.0, 0.0, 1.0)
    context.move_to((OVERLAY_FRAME_WIDTH - w) / 2.0,
                    (OVERLAY_FRAME_HEIGHT - h) / 2.0)
    context.show_text(text)


def create_pipepline(pipeline: Gst.Pipeline):
    src = Gst.ElementFactory.make("rtspsrc", "src")
    src.set_property(
        "location", "rtsp://" + config.USERNAME + ":" + config.PASSWORD + "@" + config.IPADDRESS + "/stream1")
    src.set_property("latency", 0)
    src.set_property("drop-on-latency", True)
    # src.set_property("udp-buffer-size", 2097152)

    queue = Gst.ElementFactory.make("queue", "queue")
    queue.set_property("max-size-buffers", 4)
    depay = Gst.ElementFactory.make("rtph264depay", "depay")
    parse = Gst.ElementFactory.make("h264parse", "parse")
    decode = Gst.ElementFactory.make("avdec_h264", "decode")
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    overlay = Gst.ElementFactory.make("cairooverlay", "overlay")
    overlay.connect('draw', on_draw)
    sink = Gst.ElementFactory.make("autovideosink", "sink")

    if (not src or not depay or not parse or not decode or not convert or not sink):
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    pipeline.add(src)
    pipeline.add(queue)
    pipeline.add(depay)
    pipeline.add(parse)
    pipeline.add(decode)
    pipeline.add(convert)
    pipeline.add(overlay)
    pipeline.add(sink)

    def on_rtspsrc_pad_added(rtspsrc, pad, depay):
        print(pad.name)
        src.link(queue)
        queue.link(depay)

    src.connect("pad-added", on_rtspsrc_pad_added, depay)

    ret = depay.link(parse)
    ret = ret and parse.link(decode)
    ret = ret and decode.link(convert)
    ret = ret and convert.link(overlay)
    ret = ret and overlay.link(sink)

    if not ret:
        print("ERROR: Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: Elements could be linked")

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
