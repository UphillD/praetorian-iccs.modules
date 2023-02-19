#!/bin/bash
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# Image builder & pusher

docker build --platform linux/amd64 -f Dockerfile \
	--build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
	--build-arg GIT_SHA=$(git describe --tags --match XXXXXXX --always --abbrev=40) \
	-t uphilld/praetorian:backend .
docker push uphilld/praetorian:backend
