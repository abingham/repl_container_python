FROM  alpine:latest
LABEL maintainer=austin@sixty-north.com

# Install os-provided packges
RUN apk --update --no-cache add \
bash \
gcc \
g++ \
make \
musl-dev \
python3-dev

ARG CYBER_DOJO_RUNNER_HOME
WORKDIR ${CYBER_DOJO_RUNNER_HOME}

# Install Python requirements
COPY requirements.txt ${workdir}
RUN pip3 install -r requirements.txt

# Copy over the rest of the source
COPY . ${CYBER_DOJO_RUNNER_HOME}

ARG PORT
EXPOSE ${PORT}
ENV PORT ${PORT}

CMD [ "./up.sh" ]
