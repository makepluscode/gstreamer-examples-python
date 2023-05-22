from datetime import datetime
import fsutil
import debugpy
import cairo
import os
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import gi

import config

gi.require_version('Gtk', '3.0')


class DrawingArea(Gtk.DrawingArea):

    def __init__(self, id):
        super().__init__()

        self.id = id
        self.vexpand = False
        self.hexpand = True

        self.connect("draw", self.on_draw)

    def on_draw(self, area, context):

        #debugpy.debug_this_thread()

        filename = config.DATA_PATH + "/ch%d.jpg" % self.id

        if os.path.exists(filename):
            # print("file exist")
            pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename, 800, 450, True)
        else:
            print("file not exist : %s " % filename)
            pb = GdkPixbuf.Pixbuf.new_from_file("empty.jpg")

        if pb:
            Gdk.cairo_set_source_pixbuf(context, pb, 0, 0)

        context.paint()

        return False


class MyWindow(Gtk.Window):
    count = 0

    def __init__(self):
        super().__init__(title="GTK viewer")
        self.set_size_request(1600, 1000)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.drawingArea1 = DrawingArea(1)
        self.drawingArea1.set_size_request(800, 450)
        self.drawingArea2 = DrawingArea(2)
        self.drawingArea2.set_size_request(800, 450)
        self.drawingArea3 = DrawingArea(3)
        self.drawingArea3.set_size_request(800, 450)
        self.drawingArea4 = DrawingArea(4)
        self.drawingArea4.set_size_request(800, 450)

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vertical_box)

        horizontal_box_1 = Gtk.Box()
        vertical_box.pack_start(horizontal_box_1, True, True, 0)

        horizontal_box_2 = Gtk.Box()
        vertical_box.pack_start(horizontal_box_2, True, True, 0)

        horizontal_box_1.pack_start(self.drawingArea1, True, True, 0)
        horizontal_box_1.pack_start(self.drawingArea2, True, True, 0)
        horizontal_box_2.pack_start(self.drawingArea3, True, True, 0)
        horizontal_box_2.pack_start(self.drawingArea4, True, True, 0)

        ''' 3rd Horizontal Box '''
        horizontal_box_3 = Gtk.Box()
        vertical_box.pack_start(horizontal_box_3, True, True, 16)

        self.lb1 = Gtk.Label()
        self.lb2 = Gtk.Label()
        self.lb3 = Gtk.Label()
        self.lb4 = Gtk.Label()
        horizontal_box_3.pack_start(self.lb1, True, True, 0)
        horizontal_box_3.pack_start(self.lb2, True, True, 0)
        horizontal_box_3.pack_start(self.lb3, True, True, 0)
        horizontal_box_3.pack_start(self.lb4, True, True, 0)

    def __call__(self, *args):
        self.count = self.count + 1
        self.drawingArea1.queue_draw()
        self.drawingArea2.queue_draw()
        self.drawingArea3.queue_draw()
        self.drawingArea4.queue_draw()

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        cnt_dirs, cnt_files = fsutil.get_files_all()

        # print(cnt_dirs, cnt_files, size_total)

        self.lb1.set_text("%s" % current_time)
        self.lb3.set_text("%d directories (minitues)" % cnt_dirs)
        self.lb4.set_text("%d files" % cnt_files)

        return True


def main():

    fsutil.init()

    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    interval_ms = 100
    GLib.timeout_add(interval_ms, win)

    print("Get into gtk main()")
    Gtk.main()


if __name__ == "__main__":
    main()
