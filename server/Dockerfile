FROM  debian:sid
LABEL maintainer=austin@sixty-north.com

# - - - - - - - - - - - - - - - -
# install nodejs
# tar is needed to tar-pipe test coverage out of tmpfs.
# - - - - - - - - - - - - - - - -

RUN apt-get update
RUN apt-get install -y \
    bash \
    gcc \
    python3.6 \
    python3-pip \
    tar

ARG CYBER_DOJO_RUNNER_HOME
WORKDIR ${CYBER_DOJO_RUNNER_HOME}

COPY . ${CYBER_DOJO_RUNNER_HOME}
RUN pip3 install -r requirements.txt

ARG PORT
EXPOSE ${PORT}
ENV PORT ${PORT}

CMD [ "./up.sh" ]
