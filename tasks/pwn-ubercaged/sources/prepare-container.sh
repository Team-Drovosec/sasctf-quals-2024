#!/bin/bash

docker build -t madrat/ubercaged-build . && docker run -it madrat/ubercaged-build
