import numpy as np
from gi.repository import Gst, GLib, GObject
import debugpy

import os
import sys

from pipeline import PipelineClass
from common import sample_queue, SampleWapper

""" 
gst-launch-1.0 rtspsrc location='rtsp://192.168.219.155/stream1' ! \
  rtph264depay ! h264parse ! decodebin ! videoconvert ! autovideosink
"""


def create_rtspsrc_bin(index, callback, uri):
    name = "rtspsrc-bin-%02d" % index
    bin = Gst.Bin.new(name)

    if not bin:
        print("ERROR: Unable to create bin")

    src = Gst.ElementFactory.make("rtspsrc", "src")

    src.set_property("location", uri)
    src.set_property("latency", 0)
    src.set_property("drop-on-latency", True)
    # src.set_property("udp-buffer-size", 2097152)
    # src.set_property("do-rtsp-keep-alive", 1)

    queue = Gst.ElementFactory.make("queue", "queue")
    queue.set_property("max-size-buffers", 4)
    depay = Gst.ElementFactory.make("rtph264depay", "depay")
    parse = Gst.ElementFactory.make("h264parse", "parse")
    decode = Gst.ElementFactory.make("avdec_h264", "decode")
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    videorate = Gst.ElementFactory.make("videorate", "videorate")
    caps = Gst.Caps.from_string("video/x-raw, framerate=1/1, format=RGB")

    sink = Gst.ElementFactory.make("appsink", "rtspsink-%d" % index)
    sink.set_property("emit-signals", True)
    sink.set_property("max-buffers", 4)
    sink.set_property("drop", False)
    sink.set_property("sync", False)

    if not src or not depay or not parse or not decode or not convert or not sink:
        print("ERROR: Not all elements could be created.")
        sys.exit(1)

    Gst.Bin.add(bin, src)
    Gst.Bin.add(bin, queue)
    Gst.Bin.add(bin, depay)
    Gst.Bin.add(bin, parse)
    Gst.Bin.add(bin, decode)
    Gst.Bin.add(bin, convert)
    Gst.Bin.add(bin, videorate)
    Gst.Bin.add(bin, sink)

    def on_rtspsrc_pad_added(rtspsrc, pad, depay):
        string = pad.query_caps(None).to_string()
        print(pad.name)
        src.link(queue)
        queue.link(depay)

    src.connect("pad-added", on_rtspsrc_pad_added, depay)

    ret = depay.link(parse)
    ret = ret and parse.link(decode)
    ret = ret and decode.link(convert)
    ret = ret and convert.link(videorate)
    ret = ret and videorate.link_filtered(sink, caps)

    if not ret:
        print("ERROR: Elements could not be linked")
        sys.exit(1)
    else:
        print("DONE: Elements could be linked")

    sink.connect("new-sample", callback, sink)

    return bin

def on_sample_camera_ch1(sink, data):
    # debugpy.debug_this_thread()

    gst_sample = sink.emit("pull-sample")
    sample = SampleWapper(gst_sample, 1)
    sample_queue.put(sample)

    return True


def on_on_sample_camera_ch2(sink, data):
    # debugpy.debug_this_thread()

    gst_sample = sink.emit("pull-sample")
    sample = SampleWapper(gst_sample, 2)
    sample_queue.put(sample)

    return True
