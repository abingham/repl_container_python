FROM  alpine:latest
LABEL maintainer=austin@sixty-north.com

# - - - - - - - - - - - - - - - -
# install nodejs
# tar is needed to tar-pipe test coverage out of tmpfs.
# - - - - - - - - - - - - - - - -
RUN apk --update --no-cache add \
    bash \
    gcc \
    g++ \
    make \
    musl-dev \
    python3-dev

ARG CYBER_DOJO_RUNNER_HOME
WORKDIR ${CYBER_DOJO_RUNNER_HOME}

COPY . ${CYBER_DOJO_RUNNER_HOME}

# For some reason the `python3 setup.py install` by itself fails to install some dependencies. Hmmm...
RUN pip3 install -e .
RUN python3 setup.py install

ARG PORT
EXPOSE ${PORT}
ENV PORT ${PORT}

CMD [ "./up.sh" ]
