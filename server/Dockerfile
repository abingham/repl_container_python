FROM  cyberdojo/repl_container_python_base
LABEL maintainer=austin@sixty-north.com

ARG CYBER_DOJO_RUNNER_HOME
WORKDIR ${CYBER_DOJO_RUNNER_HOME}

COPY . ${CYBER_DOJO_RUNNER_HOME}

ARG PORT
EXPOSE ${PORT}
ENV PORT ${PORT}

CMD [ "./up.sh" ]
