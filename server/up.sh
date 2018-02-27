#!/bin/sh

cd src
python3 -m repl_container_python -vv --port $PORT --host 0.0.0.0
