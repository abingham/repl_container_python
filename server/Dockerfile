FROM  docker:latest
LABEL maintainer=austin@sixty-north.com

# - - - - - - - - - - - - - - - -
# install nodejs
# tar is needed to tar-pipe test coverage out of tmpfs.
# - - - - - - - - - - - - - - - -

RUN apk --update --no-cache add \
bash \
python3 \
tar

ARG            CYBER_DOJO_RUNNER_HOME
WORKDIR      ${CYBER_DOJO_RUNNER_HOME}

# - - - - - - - - - - - - - - - -
# setup server
# - - - - - - - - - - - - - - - -

COPY . ${CYBER_DOJO_RUNNER_HOME}
RUN pip3 install -r requirements.txt

ARG PORT
EXPOSE ${PORT}
ENV PORT ${PORT}

CMD [ "./up.sh" ]
