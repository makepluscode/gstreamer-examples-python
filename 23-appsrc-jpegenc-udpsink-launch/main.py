import numpy as np
import os

from gi.repository import Gst, GObject, GLib

import sys
import gi
gi.require_version('Gst', '1.0')

import time

appsrc = None

PIPELINE_TEST = '''
videotestsrc !
videoconvert !
clockoverlay time-format='%D %H:%M:%S' ! \
jpegenc quality=85 ! \
rtpjpegpay !
udpsink host=127.0.0.1 port=5000
'''

PIPELINE = '''
appsrc name=source emit-signals=True is-live=True caps=video/x-raw,format=RGB,width=640,height=480,framerate=30/1 ! \
queue max-size-buffers=4 ! \
videoconvert  ! \
video/x-raw, format=YUY2 ! \
clockoverlay time-format='%D %H:%M:%S' ! \
jpegenc quality=85 ! \
rtpjpegpay type=2 !
udpsink host=127.0.0.1 port=5000
'''

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
    time.sleep(1)
    ndarray = np.full((640, 480, 3), 0, dtype=np.uint8)
    buffer = Gst.Buffer.new_wrapped(ndarray.tobytes())
    gst_flow_return = src.emit("push-buffer",  buffer)

    if gst_flow_return != Gst.FlowReturn.OK:
        print('error')


def stop_feed():
    print("stop feed")


def main():
    Gst.init(sys.argv)

    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(3)

    pipeline = Gst.parse_launch(PIPELINE)

    global appsrc
    appsrc = pipeline.get_by_name('source')
    appsrc.set_property("format", Gst.Format.TIME)
    appsrc.set_property('do-timestamp', True)
    appsrc.connect('need-data', start_feed)
    appsrc.connect('enough-data', stop_feed)

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
