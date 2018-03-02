#!/bin/sh

cd src
python3 -m repl_container_python \
        -v \
        --port $PORT \
        --host 0.0.0.0
