FROM  alpine:latest
LABEL maintainer=austin@sixty-north.com

# - - - - - - - - - - - - - - - -
# install nodejs
# tar is needed to tar-pipe test coverage out of tmpfs.
# - - - - - - - - - - - - - - - -
RUN apk --update --no-cache add \
    bash \
    gcc \
    make \
    musl-dev \
    python3-dev \
    tar

ARG CYBER_DOJO_RUNNER_HOME
WORKDIR ${CYBER_DOJO_RUNNER_HOME}

COPY . ${CYBER_DOJO_RUNNER_HOME}
RUN pip3 install -r requirements.txt

ARG PORT
EXPOSE ${PORT}
ENV PORT ${PORT}

CMD [ "./up.sh" ]
