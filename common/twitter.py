#!/usr/bin/env python3
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# Twitter related functionality (API v2)

import os
import sys

import requests

from configparser import ConfigParser
from loguru import logger

####################
## INITIALIZATION ##
####################
# Read configuration
config = ConfigParser()
config.read('/app/praetorian-backend/config.ini')

# Set query parameters
query_params = {
	'tweet.fields'	: config['Twitter']['tweet.fields'],
	'user.fields'	: config['Twitter']['user.fields'],
	'media.fields'	: config['Twitter']['media.fields'],
	'poll.fields'	: config['Twitter']['poll.fields'],
	'place.fields'	: config['Twitter']['place.fields'],
	'expansions'	: config['Twitter']['expansions']
}

###############
## FUNCTIONS ##
###############
# Generates an authentication object via bearer token
def bearer_oauth(r):
	# Grab the credential from the enviroment variable
	bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
	if not bearer_token:
		logger.error('Failed to grab bearer token from environment variable.')
		sys.exit(config['Exit Codes'].getint('missing_credentials'))
	# Fill the headers
	r.headers['Authorization'] = f'Bearer {bearer_token}'
	r.headers['User-Agent'] = 'v2FilteredStreamPython'
	return(r)

# Gets current query rules from Twitter
def get_rules():
	logger.log('COMM', 'Quering Twitter for current crawling rules...')
	r = requests.get(config['URLs']['twitter_rules'], auth=bearer_oauth)
	try:
		r.raise_for_status()
	except:
		logger.warn('Query failed (HTTP {}).'.format(r.status_code))
		logger.warn('Message: {}.'.format(r.text))
		return(None)
	logger.success('{} old rules received from Twitter.'.format(r.json()['meta']['result_count']))
	return(r.json())

# Deletes current query rules on Twitter
def delete_rules(rules):
	# Map existing rules to list
	try:
		ids = list(map(lambda rule: rule['id'], rules['data']))
	except:
		logger.warn('No preexisting rules detected, skipping rule deletion.')
		return(None)
	logger.log('COMM', 'Quering Twitter to delete current crawling rules...')
	r = requests.post(config['URLs']['twitter_rules'], auth=bearer_oauth, json={ 'delete' : { 'ids' : ids } })
	try:
		r.raise_for_status()
	except:
		logger.warn('Query failed (HTTP {}).'.format(r.status_code))
		logger.warn('Message: {}.'.format(r.text))
		return(None)
	logger.success('{} old rules deleted on Twitter.'.format(r.json()['meta']['summary']['deleted']))
	if r.json()['meta']['summary']['not_deleted']:
		logger.warn('{} old rules not deleted.'.format(r.json()['meta']['summary']['not_deleted']))
	return(r.json())

# Sets new query rules
def set_rules(rules):
	logger.log('COMM', 'Quering Twitter to set new crawling rules...')
	r = requests.post(config['URLs']['twitter_rules'], auth=bearer_oauth, json={ 'add' : rules })
	try:
		r.raise_for_status()
	except:
		logger.error('Query failed (HTTP {})'.format(r.status_code))
		logger.error('Message: {}.'.format(r.text))
		sys.exit(config['Exit Codes'].getint('twitter_post'))
	logger.success('{} new rules set on Twitter.'.format(r.json()['meta']['summary']['created']))
	return(r.json())
