FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt -y upgrade && \
    apt install -y file sudo build-essential curl git lsb-base lsb-release apt-utils libgdk-pixbuf2.0-0 libatk1.0-0 fonts-liberation libxcomposite1 libpango-1.0-0 libxext6 xdg-utils libx11-6 libcups2 libexpat1 libxcb1 libxss1 libdbus-1-3 libgbm1 libgtk-3-0 libpangocairo-1.0-0 libxdamage1 libatspi2.0-0 libxfixes3 libatk-bridge2.0-0 libxi6 libxrender1 libxcursor1 libnss3 libglib2.0-0 libasound2 ca-certificates libgcc1 libnspr4 libxtst6 libcairo2 libx11-xcb1 libdrm2 wget libxrandr2 libxcb-dri3-0 libc6 libappindicator3-1 netcat curl libvulkan1 libu2f-udev

RUN groupadd -g 1000 pwn && useradd -g pwn -m -u 1000 pwn -s /bin/bash

COPY ./ubercaged /ubercaged

RUN dpkg -i /ubercaged/chromium-browser-unstable_120.0.6099.228-1_amd64.deb

USER pwn

# just for tests
# RUN chromium-browser-unstable --no-sandbox --headless --disable-gpu --virtual-time-budget=60000 http://192.168.1.66:8000/pwn.html

CMD ["bash"]

# docker build -t madrat/ubercaged .
# docker run -it --name ubercaged madrat/ubercaged

# Run chrome inside docker
# chromium-browser-unstable --no-sandbox --headless --disable-gpu --virtual-time-budget=60000 http://127.0.0.1:8000/pwn.html

# Run server with exploit
# python3 -m http.server

# run listener (if required, recreate shellcode using generate_shellcode.py)
# sudo nc -lvp 1337