#!/bin/bash
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# Image launcher

docker run -dit --env-file credentials.env --log-driver local --name praetorian-backend --network host --restart unless-stopped uphilld/praetorian:backend
docker logs -f praetorian-backend &> praetorian-backend.log &
