#!/bin/bash
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# Docker image entrypoint

# Grab the credentials
cd /app/praetorian-backend

# Define function that displays help message
function help_msg () {
	if [ "$1" = "error" ]; then
		echo -e 'Non standard arguments detected.'
	fi
	echo -e 'Usage:'
	echo -e '\t docker run -dit [--env LOADML="true"] --env-file credentials.env [--gpus all] --log-driver local --name praetorian_backend --network host --restart unless-stopped uphilld/praetorian:backend'
	echo -e ''
	echo -e 'Optional Parameters:'
	echo -e '\t --env LOADML="true"\t: Use this to enable the loading of the classification models'
	echo -e '\t --gpus all\t\t: Use this to enable utilization of GPU (Nvidia GPU required)'
	echo -e ''
	echo -e 'Print log:'
	echo -e '\t docker logs praetorian_backend'
	echo -e ''
}

# Launch all (no arguments)
if [ $# -eq 0 ]; then
	python3 -u main.py
# Conditional launch (one argument)
elif [ $# -eq 1 ]; then
	case "$1" in
	"bash")	exec /bin/bash ;;
	"help") help_msg ;;
	*)		help_msg 'error' ;;
	esac
else
	help_msg 'error'
fi
