#!/bin/sh

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, media=video, encoding-name=JPEG, framerate=30/1, payload=26, clock-rate=90000 ! rtpjpegdepay ! jpegdec ! videoconvert ! autovideosink