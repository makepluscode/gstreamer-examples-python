# gstreamer-examples-python
Gstreamer examples written by in Python

### Python version

```
# python --version
Python 3.8.10
```

### Gstremer dependencies
```
# dpkg -l | grep gstreamer
ii  gir1.2-gstreamer-1.0:amd64             1.16.3-0ubuntu1.1                     amd64        GObject introspection data for the GStreamer library
ii  gstreamer1.0-alsa:amd64                1.16.3-0ubuntu1.1                     amd64        GStreamer plugin for ALSA
ii  gstreamer1.0-doc                       1.16.3-0ubuntu1.1                     all          GStreamer core documentation and manuals
ii  gstreamer1.0-gl:amd64                  1.16.3-0ubuntu1.1                     amd64        GStreamer plugins for GL
ii  gstreamer1.0-gtk3:amd64                1.16.3-0ubuntu1.1                     amd64        GStreamer plugin for GTK+3
ii  gstreamer1.0-libav:amd64               1.16.2-2                              amd64        ffmpeg plugin for GStreamer
ii  gstreamer1.0-plugins-bad:amd64         1.16.3-0ubuntu1                       amd64        GStreamer plugins from the "bad" set
ii  gstreamer1.0-plugins-bad-dbg:amd64     1.16.3-0ubuntu1                       amd64        GStreamer plugins from the "bad" set (debug symbols)
ii  gstreamer1.0-plugins-bad-doc           1.16.3-0ubuntu1                       all          GStreamer documentation for plugins from the "bad" set
ii  gstreamer1.0-plugins-base:amd64        1.16.3-0ubuntu1.1                     amd64        GStreamer plugins from the "base" set
ii  gstreamer1.0-plugins-base-apps         1.16.3-0ubuntu1.1                     amd64        GStreamer helper programs from the "base" set
ii  gstreamer1.0-plugins-base-dbg:amd64    1.16.3-0ubuntu1.1                     amd64        GStreamer plugins from the "base" set
ii  gstreamer1.0-plugins-base-doc          1.16.3-0ubuntu1.1                     all          GStreamer documentation for plugins from the "base" set
ii  gstreamer1.0-plugins-good:amd64        1.16.3-0ubuntu1.1                     amd64        GStreamer plugins from the "good" set
ii  gstreamer1.0-plugins-good-dbg:amd64    1.16.3-0ubuntu1.1                     amd64        GStreamer plugins from the "good" set
ii  gstreamer1.0-plugins-good-doc          1.16.3-0ubuntu1.1                     all          GStreamer documentation for plugins from the "good" set
ii  gstreamer1.0-plugins-rtp               1.14.4.1                              amd64        GStreamer elements from the "rtp" set
ii  gstreamer1.0-plugins-ugly:amd64        1.16.2-2build1                        amd64        GStreamer plugins from the "ugly" set
ii  gstreamer1.0-plugins-ugly-dbg:amd64    1.16.2-2build1                        amd64        GStreamer plugins from the "ugly" set (debug symbols)
ii  gstreamer1.0-plugins-ugly-doc          1.16.2-2build1                        all          GStreamer documentation for plugins from the "ugly" set
ii  gstreamer1.0-pulseaudio:amd64          1.16.3-0ubuntu1.1                     amd64        GStreamer plugin for PulseAudio
ii  gstreamer1.0-qt5:amd64                 1.16.3-0ubuntu1.1                     amd64        GStreamer plugin for Qt5
ii  gstreamer1.0-tools                     1.16.3-0ubuntu1.1                     amd64        Tools for use with GStreamer
ii  gstreamer1.0-x:amd64                   1.16.3-0ubuntu1.1                     amd64        GStreamer plugins for X11 and Pango
ii  libgstreamer-gl1.0-0:amd64             1.16.3-0ubuntu1.1                     amd64        GStreamer GL libraries
ii  libgstreamer-opencv1.0-0:amd64         1.16.3-0ubuntu1                       amd64        GStreamer OpenCV libraries
ii  libgstreamer-plugins-bad1.0-0:amd64    1.16.3-0ubuntu1                       amd64        GStreamer libraries from the "bad" set
ii  libgstreamer-plugins-bad1.0-dev:amd64  1.16.3-0ubuntu1                       amd64        GStreamer development files for libraries from the "bad" set
ii  libgstreamer-plugins-base1.0-0:amd64   1.16.3-0ubuntu1.1                     amd64        GStreamer libraries from the "base" set
ii  libgstreamer-plugins-base1.0-dev:amd64 1.16.3-0ubuntu1.1                     amd64        GStreamer development files for libraries from the "base" set
ii  libgstreamer-plugins-good1.0-0:amd64   1.16.3-0ubuntu1.1                     amd64        GStreamer development files for libraries from the "good" set
ii  libgstreamer-plugins-good1.0-dev       1.16.3-0ubuntu1.1                     amd64        GStreamer development files for libraries from the "good" set
ii  libgstreamer1.0-0:amd64                1.16.3-0ubuntu1.1                     amd64        Core GStreamer libraries and elements
ii  libgstreamer1.0-dev:amd64              1.16.3-0ubuntu1.1                     amd64        GStreamer core development files
ii  libqt5gstreamer-1.0-0:amd64            1.2.0-5                               amd64        C++ bindings library for GStreamer with a Qt-style API - Qt 5 build
```
