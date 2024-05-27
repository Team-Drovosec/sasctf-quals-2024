FROM debian:bullseye

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update -y && \
    apt install -y wget

WORKDIR /work

RUN wget -c https://github.com/python/cpython/archive/refs/tags/v3.12.3.tar.gz -O - | \
    tar -xz

RUN apt update -y && \
    apt install -y build-essential gdb lcov pkg-config \
    libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
    libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
    lzma lzma-dev tk-dev uuid-dev zlib1g-dev

ADD patch/opcode_ids.h.new cpython-3.12.3/include/opcode_ids.h

RUN cd cpython-3.12.3 && \
    ./configure && \
    make && \
    make test && \
    make install

ENV PATH /work/cpython-3.12.3:$PATH
