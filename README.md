# PolyLive

This repository holds the code implementing the PolyLive system, as well as the data used to evaluate it. Make sure to install the submodules through `git submodule update --init --recursive`.
The `start_demo.sh` script can be used to build and launch the system. A web-demo is then available on port 5000 of localhost. Alternatively, you can connect to the docker console ( `docker exec -it polylive bash` ) and then launch the system on any file using the `src/launcher/launcher.py` script.