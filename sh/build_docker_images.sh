#!/bin/bash

readonly ROOT_DIR="$( cd "$( dirname "${0}" )" && cd .. && pwd )"

docker build -t cyberdojo/repl_container_python_base -f ${ROOT_DIR}/server/Dockerfile.base ${ROOT_DIR}/server
docker-compose --file ${ROOT_DIR}/docker-compose.yml build
