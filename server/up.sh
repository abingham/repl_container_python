#!/bin/sh

cd src
python3 -m web_app -vv --port $PORT --host 0.0.0.0
