#!/usr/bin/env python3
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# Image recipe

# Pull base tf image
FROM tensorflow/tensorflow:2.9.1-gpu

# Set working directory
WORKDIR /app

# Install packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends -q \
	build-essential \
	bash git vim wget \
	openjdk-8-jdk-headless \
	openssh-client \
	libopencv-dev python3-opencv \
	python3 \
	python3-pip python3-setuptools python3-six \
	python3-numpy python3-pandas \
 && apt-get autoremove -y -q \
 && apt-get clean -y -q \
 && apt-get autoclean -y -q \
 && rm -rf /var/lib/apt/lists/*

# Set enviroment variables
ENV SPARK_HOME="/app/spark-3.0.2-bin-hadoop2.7"
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"

# Install NLU prerequisites
RUN wget -nv "https://archive.apache.org/dist/spark/spark-3.0.2/spark-3.0.2-bin-hadoop2.7.tgz" \
 && tar -xf spark-3.0.2-bin-hadoop2.7.tgz \
 && rm -rf spark-3.0.2-bin-hadoop2.7.tgz

# Install Python requirements
COPY requirements.txt .
RUN pip3 install --upgrade --no-cache-dir -q -r requirements.txt \
 && rm requirements.txt

# Copy ML models
COPY external/models /app/models

# Copy NLU cache
COPY external/cache /root

# Clone git repo
# The ARG command is here to force the cloning
ARG GIT_SHA
COPY external/github-key /
RUN chmod 600 /github-key \
 && echo "IdentityFile /github-key" >> /etc/ssh/ssh_config \
 && echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config \
 && git clone --depth 1 git@github.com:UphillD/praetorian-backend.git

# Set timezone
ENV TZ="Europe/Athens"

# Set entrypoint
ENTRYPOINT ["/app/praetorian-backend/build/entrypoint.sh"]

# Set healthcheck
HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=5 CMD /bin/bash -c "[ -f /app/ready ]"

# Set labels according to Label Schema Convention
# http://label-schema.org/rc1/
ARG BUILD_DATE
LABEL maintainer "Antonios Karteris <akarteris@microlab.ntua.gr>"
LABEL org.label-schema.build-date $BUILD_DATE
LABEL org.label-schema.name "Praetorian | WP6 T4 | Backend"
LABEL org.label-schema.description "Praetorian H2020 Project | Work Package 6 : Response Coordination | Task 4 : Integration with Social Media | Backend Implementation"
LABEL org.label-schema.usage "/docs/README.md"
LABEL org.label-schema.url "https://praetorian-h2020.eu/"
LABEL org.label-schema.vcs-url "https://github.com/Uphilld/praetorian-backend"
LABEL org.label-schema.vcs-ref $GIT_SHA
LABEL org.label-schema.vendor "Institute of Communication and Computer Systems (ICCS)"
LABEL org.label-schema.version "RC"
LABEL org.label-schema.schema-version "1.0"
LABEL org.label-schema.docker.cmd "docker run -dit [--env LOADML='true'] --env-file credentials.env [--gpus all] --log-driver local --name praetorian_backend --network host --restart unless-stopped uphilld/praetorian:backend"
LABEL org.label-schema.docker.cmd.devel "docker exec -it praetorian_backend /bin/bash"
LABEL org.label-schema.docker.cmd.help "docker exec -it praetorian_backend /app/praetorian-backend/build/entrypoint.sh help"
