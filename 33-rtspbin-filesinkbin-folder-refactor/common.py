import numpy as np
from gi.repository import Gst, GLib, GObject
import debugpy
import numpy as np
import queue

# global variables
sample_queue = queue.Queue()


class SampleWapper:
    camera = -1
    sample = None

    def __init__(self, sample, camera) -> None:
        self.sample = sample
        self.camera = camera
