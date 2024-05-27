#!/bin/sh

echo "127.0.0.1 einabe.local" > /etc/hosts
nginx &
redis-server /etc/redis.conf &
python main.py