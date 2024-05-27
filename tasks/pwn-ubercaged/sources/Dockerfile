from ubuntu:22.04

RUN \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && apt-get update -y

RUN \
    apt install -y file sudo build-essential curl git lsb-base lsb-release apt-utils libgdk-pixbuf2.0-0 libatk1.0-0 fonts-liberation libxcomposite1 libpango-1.0-0 libxext6 xdg-utils libx11-6 libcups2 libexpat1 libxcb1 libxss1 libdbus-1-3 libgbm1 libgtk-3-0 libpangocairo-1.0-0 libxdamage1 libatspi2.0-0 libxfixes3 libatk-bridge2.0-0 libxi6 libxrender1 libxcursor1 libnss3 libglib2.0-0 libasound2 ca-certificates libgcc1 libnspr4 libxtst6 libcairo2 libx11-xcb1 libdrm2 wget libxrandr2 libxcb-dri3-0 libc6 libappindicator3-1

RUN useradd --create-home -g root -G sudo -u 1001 chrome
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
WORKDIR /home/chrome
USER chrome

RUN cd /home/chrome \
    && git clone https://github.com/pwndbg/pwndbg \
    && cd ./pwndbg \
    && ./setup.sh

# Get the source code
RUN cd /home/chrome && git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git

ENV PATH=/home/chrome/depot_tools:$PATH

# This is ugly but it needs to be done in one RUN as otherwise the build will fail. 
# See: https://groups.google.com/a/chromium.org/g/chromium-dev/c/Sa3_-7tKR0E
RUN mkdir ./chromium && cd ./chromium \
    && fetch --nohooks --no-history chromium \
    && cd src \
    && ./build/install-build-deps.sh --no-prompt --no-nacl --no-arm --no-chromeos-fonts \
    && git fetch --tags \
    && git checkout tags/120.0.6099.228 \
    && cd /home/chrome/chromium/src/v8 \
    && gclient sync

COPY ./prerequisites /home/chrome/prerequisites
RUN cd /home/chrome/chromium/src/v8 \
    && git apply /home/chrome/prerequisites/pwn.diff

RUN /home/chrome/prerequisites/build_chrome_debug.sh \
    && /home/chrome/prerequisites/build_chrome_release.sh

ENTRYPOINT ["/bin/bash"]