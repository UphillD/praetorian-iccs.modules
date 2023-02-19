#!/usr/bin/env python3
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# CO-specific functionality

import cv2
import numpy
import re
import urllib

tag_rules = 'lexicon_CO'
tag_identifiers = ''
tag_tweets = 'CO_tweets'
a = 2
b = 3

#########################
## AUXILIARY FUNCTIONS ##
#########################
# Cleans up tweet text
def cleanup_text(text):
	text = text.replace('Disclaimer: This tweet contains false information.', '')	# Remove disclaimer
	text = re.sub(r'@\S+', '', text)												# Remove mentions
	text = re.sub(r'http\S+', '<link>', text)										# Remove URLs
	text = re.sub(r'[\W]', ' ', text)												# Remove symbols
	text = ' '.join(text.split())													# Remove duplicate spaces
	text = text.strip()																# Remove heading or trailing spaces
	return(text)

# Classifies a tweet's text
def classify_text(text, model):
	# Clean text
	text = [ cleanup_text(text) ]
	# Make prediction
	prediction = model.predict(text)
	# Return boolean classification
	return(prediction.iat[0, 2] == 'informative')

# Classifies a tweet's image
def classify_image(image_url, model):
	# Open image
	r = urllib.request.urlopen(image_url)
	# Transform image to numpy array
	a = numpy.asarray(bytearray(r.read()), dtype=numpy.uint8)
	# Expand image dimensions from 3 to 4
	image = numpy.expand_dims(cv2.imdecode(a, -1), axis=0)
	# Make prediction
	prediction = model.predict(image)
	# Return boolean classification
	return(prediction[0][0] == 1.0)

#############################
## CLASSIFICATION FUNCTION ##
#############################
def classifyTweet(tweet, _, text_model, image_model):

	####################
	## INITIALIZATION ##
	####################
	classification = False

	#####################
	## DATA EXTRACTION ##
	#####################
	text = tweet['data']['text']
	media = tweet['includes']['media'] of 'media' in tweet['includes'] else None

	####################
	## CLASSIFICATION ##
	####################
	# Text classification
	classification = classify_text(text, text_model):
	# Image classification
	if not classification and media:
		for media_item in media:
			classification = classify_image(media_item['url'], image_model)
			if classification:
				break

	#############
	## TAGGING ##
	#############
	# Surround words matching crawling rules with '$'
	already_tagged = []
	for rule in tweet['matching_rules']:
		for word in rule['tag'].split():
			if word != '&' and word not in already_tagged:
				already_tagged.append(word)
				text = text.replace(word, '$' + word + '$')

	return(classification, 'low', text, None)
