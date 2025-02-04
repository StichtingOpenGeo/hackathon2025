# SIP client

This is the first boilerplate for a SIP client that can receive and send raw audio datastreams, instead of using a hardware device or a fixed WAV-file.
The source code will be changed to include the functionality as laid out in the initial design document.

## Prerequisites

- Python 3.12
- numpy
- pjsau2
- edge_tts
- pydub

## Quickstart

- Clone this repository (`e.g. git clone git@github.com:StichtingOpenGeo/hackathon2025.git`) and `cd` into the "sipclient" folder.
- Make sure you have the basic development tools such as make, autoconf and gcc installed.
- ```pip install numpy edge_tts pydub
  git clone --depth=1 git@github.com:pjsip/pjproject.git
  cd pjproject
  CFLAGS="-O2 -fPIC" CXXFLAGS="-O2 -fPIC" ./configure
  make dep
  make -j5
  cd pjsip-apps/src/swig/pyhon
  make
  pip install .
  ```
- Configure SIP_USERNAME, SIP_DOMAIN and SIP_PASSWORD in config.py 

## TODO

1. Incorporate whisper_cpp, with streaming functionality.
2. Add the barge-in detection.
3. Decide the best architecture for interfacing with langchain, doing it within this project or outside.
