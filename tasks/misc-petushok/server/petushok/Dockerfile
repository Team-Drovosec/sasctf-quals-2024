FROM bad_python

WORKDIR /work

RUN apt update -y && \
    apt install -y curl

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py

RUN python -m pip install flask
RUN python -m pip install gunicorn

WORKDIR /app

ADD app .
ADD scripts/helper.py .

RUN python -m compileall -b

RUN rm helper.py
