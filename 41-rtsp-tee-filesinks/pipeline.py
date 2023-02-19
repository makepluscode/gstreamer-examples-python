from gi.repository import Gst, GLib, GObject

import debugpy
import os

import config


class PipelineClass(object):
    _instance = None
    _pipeline = None

    def __init__(self):
        raise RuntimeError('call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._pipeline = Gst.Pipeline()
            if not cls._pipeline:
                raise RuntimeError("fail to create a pipeline")

            cls._instance = cls.__new__(cls)
        return cls._instance

    def add_bin(self, bin):
        print(type(self._pipeline))
        self._pipeline.add(bin)

    def start(self, loop):
        self._pipeline.set_state(Gst.State.PLAYING)

        # connect bus to catch signal from the pipeline
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", on_message, loop)

    def stop(self):
        self._pipeline.set_state(Gst.State.NULL)

    def get_element(self, name):
        return self._pipeline.get_by_name(name)


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
    else:
        msg_struct = message.get_structure()
        if msg_struct:
            if msg_struct.get_name() == "GstMultiFileSink":
                success, index = msg_struct.get_int("index")
                file_path = msg_struct.get_string("filename")

                if 'ch01' in file_path:
                    link_path = config.DATA_PATH + "/ch1.jpg"
                if 'ch02' in file_path:
                    link_path = config.DATA_PATH + "/ch2.jpg"
                if 'ch03' in file_path:
                    link_path = config.DATA_PATH + "/ch3.jpg"
                if 'ch04' in file_path:
                    link_path = config.DATA_PATH + "/ch4.jpg"

                if os.path.exists(link_path):
                    os.remove(link_path)
                os.symlink(file_path, link_path)

    return True


def graph_pipeline(pipeline):
    Gst.debug_bin_to_dot_file(pipeline, Gst.DebugGraphDetails.ALL, "pipeline")
    try:
        os.system("dot -Tpng -o ./pipeline.png ./pipeline.dot")
    except Exception as e:
        print(e)
