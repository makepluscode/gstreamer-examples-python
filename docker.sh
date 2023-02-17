docker run --gpus all -it --rm \
  -v $(pwd):/git \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=unix$DISPLAY \
  tensorrt