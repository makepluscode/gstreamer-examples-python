from pipeline import PipelineClass
import sink_bin
import source_bin
import fsutil
import sys
import config
import debugpy
from gi.repository import Gst, GLib, GObject
import gi

gi.require_version("Gst", "1.0")


def main():
    Gst.init(sys.argv)

    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(3)

    fsutil.init()

    pipeline = PipelineClass.instance()

    # 1st bin : RTSP camera 1
    source1 = source_bin.create_rtspsrc_bin(
        0, source_bin.on_sample_camera_ch1, "rtsp://" + config.USERNAME + ":" + config.PASSWORD + "@" + config.IPADDRESS + "/stream1")
    pipeline.add_bin(source1)

    # 2nd bin : RTSP camera 2
    source2 = source_bin.create_rtspsrc_bin(
        1, source_bin.on_on_sample_camera_ch2, "rtsp://" + config.USERNAME + ":" + config.PASSWORD + "@" + config.IPADDRESS + "/stream1")
    pipeline.add_bin(source2)

    # 3nd bin : Jpeg encoding and filesink
    sink1 = sink_bin.create_sink_bin()
    pipeline.add_bin(sink1)

    loop = GLib.MainLoop()

    pipeline.start(loop)

    # run
    try:
        loop.run()
    except:
        pass

    # if fails, then stop
    pipeline.stop()


if __name__ == "__main__":
    main()
