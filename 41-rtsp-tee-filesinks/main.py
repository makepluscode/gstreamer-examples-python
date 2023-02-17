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
        0, source_bin.on_sample_camera_ch1, "rtsp://" + config.SRC1_USERNAME + ":" + config.SRC1_PASSWORD + "@" + config.SRC1_IPADDRESS + "/stream1")
    pipeline.add_bin(source1)

    # 2nd bin : RTSP camera 2
    source2 = source_bin.create_rtspsrc_bin(
        1, source_bin.on_sample_camera_ch2, "rtsp://" + config.SRC2_USERNAME + ":" + config.SRC2_PASSWORD + "@" + config.SRC2_IPADDRESS + "/stream1")
    pipeline.add_bin(source2)

    # 3rd bin : RTSP camera 3
    source3 = source_bin.create_rtspsrc_bin(
        2, source_bin.on_sample_camera_ch3, "rtsp://" + config.SRC3_USERNAME + ":" + config.SRC3_PASSWORD + "@" + config.SRC3_IPADDRESS + "/stream1")
    pipeline.add_bin(source3)

    # 4th bin : RTSP camera 4
    source4 = source_bin.create_rtspsrc_bin(
        3, source_bin.on_sample_camera_ch4, "rtsp://" + config.SRC4_USERNAME + ":" + config.SRC4_PASSWORD + "@" + config.SRC4_IPADDRESS + "/stream1")
    pipeline.add_bin(source4)

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
