#!/bin/sh

uvicorn local_run:app --host 10.0.0.0 --port 5000 --workers 2 >stdout 2>stderr &

uvicorn metrics:app --host 10.0.0.0 --port 31337 --workers 1 >/dev/null 2>/dev/null &

python3 kek.py >/dev/null 2>/dev/null &
