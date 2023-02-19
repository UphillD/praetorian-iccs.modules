#!/usr/bin/env python3
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# Main process

import time
t_start = time.perf_counter()

import array
import json
import os
import sys

import keras
import nlu
import requests
import touch

from configparser import ConfigParser
from loguru import logger

from common import iop
from common import twitter


###############################
## CLASSIFIER INITIALIZATION ##
###############################
# Initializes text classifier (NLU)
def init_text_classifier():
	time_start = time.perf_counter()
	try:
		model = nlu.load(path=config['Models']['text_model_path'])
	except Exception as e:
		logger.error('Failed to load text classification model.')
		logger.error('Exception: {}.'.format(e))
		sys.exit(config['Exit Codes'].getint('missing_file'))
	logger.success('Text classification model loaded in {:.2f} seconds.'.format(time.perf_counter() - time_start))
	return(model)

# Initializes image classifier (Keras)
def init_image_classifier():
	time_start = time.perf_counter()
	try:
		model = keras.models.load_model(config['Models']['image_model_path'])
	except Exception as e:
		logger.error('Failed to load image classification model.')
		logger.error('Exception: {}.'.format(e))
		sys.exit(config['Exit Codes'].getint('missing_file'))
	logger.success('Image classification model loaded in {:.2f} seconds.'.format(time.perf_counter() - time_start))
	return(model)

###################
## MAIN FUNCTION ##
###################
if __name__ == '__main__':

	###################
	## CONFIGURATION ##
	###################
	# Read configuration file
	config = ConfigParser()
	config.read('/app/praetorian-backend/config.ini')

	# Configure timezone
	time.tzset()

	# Configure loguru
	logger.level('COMM', no=15, color='<magenta>', icon='📡')
	logger.level('BYE', no=15, color='<fg #808080>', icon='🚪')
	logger.configure(handlers=[
		dict(sink=sys.stderr, colorize=True, format=config['Loguru']['format']),
		dict(sink=open('/app/main.log', 'w'), colorize=True, format=config['Loguru']['format'])
	])

	# Initialize tweet counter array
	# SMSTD Crawled | SMSTD Suspicious | CO Crawled | CO Informative
	# type: unsigned short (max 65535)
	cnt = array.array('H', [0, 0, 0, 0])

	# Initialize classification models
	text_model = init_text_classifier() if os.getenv('LOADML') else None
	image_model = init_image_classifier() if os.getenv('LOADML') else None

	# Initialize status flag
	status = False

	# Touch healthcheck file
	touch.touch('/app/ready')

	t_ready = time.perf_counter()
	logger.info('Process initialized in {:.2f} seconds.'.format(t_ready - t_start))
	logger.info('Process ready.')

	###############
	## MAIN LOOP ##
	###############
	while(True):

		if not status:
			time.sleep(1)
			status = iop.get_status(status)
		else:
			if status == 'SMSTD':
				from common.SMSTD import *
			elif status == 'CO':
				from common.CO import *
			else:
				logger.error('Received false status flag from IOP: {}.'.format(status))
				sys.exit(config['Exit Codes'].getint('false_status'))
			logger.info('{} process starting...'.format(status))
			# Get current rules from IOP
			rules = iop.get_rules(tag_rules)
			# Get old rules from twitter
			old_rules = twitter.get_rules()
			# Delete old rules from twitter
			twitter.delete_rules(old_rules)
			# Set new rules on twitter
			twitter.set_rules(rules)
			# Get CI identifiers from IOP
			identifiers = iop.get_identifiers(tag_identifiers) if status == 'SMSTD' else None

			# Initiate twitter stream
			r = requests.get(config['URLs']['twitter_stream'], auth=twitter.bearer_oauth, params=twitter.query_params, stream=True)
			try:
				r.raise_for_status()
			except:
				logger.error('Failed initiating twitter stream (HTTP {}).'.format(r.status_code))
				logger.error('Message: {}.'.format(r.text))
				sys.exit(config['Exit Codes'].getint('twitter_get_stream'))
			logger.success('Initiating twitter stream...')
			# Stream, each line is a tweet
			for line in r.iter_lines():
				if line:
					cnt[a] += 1
					# Load tweet object
					tweet = json.loads(line)
					for rule in tweet['matching_rules']:
						logger.info('Crawling rule matched: {}.'.format(rule['tag']))
					# Classify tweet as pertinent or not
					classification, priority, annotated_text, matched_identifiers = classifyTweet(tweet, identifiers, text_model, image_model)
					if classification:
						for identifier in matched_identifiers:
							logger.info('CI identifier matched: {}.'.format(identifier))
						cnt[b] += 1
						# Format tweet object for IOP storing
						del tweet['matching_rules']
						del tweet['data']['author_id']
						del tweet['data']['edit_history_tweet_ids']
						tweet['data']['text'] = tweet['data']['text'].replace('Disclaimer: This tweet contains false information.', '')
						tweet['data']['text_annotated'] = annotated_text
						tweet['data']['url'] = 'https://twitter.com/' + tweet['includes']['users'][0]['username'] + '/status/' + tweet['data']['id']
						payload = json.dumps({ 'tweet': tweet, 'text': annotated_text, 'priority': priority, 'collection': tag_tweets })
						iop.register_tweet(payload)
					logger.info('{} tweets crawled, of which {} identified as pertinent'.format(cnt[a], cnt[b]))
				# Recheck running flag
				next_status = iop.get_status(status)
				if status != next_status:
					status = next_status
					logger.info('Process stopped, idling...')
					break
