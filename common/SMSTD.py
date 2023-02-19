#!/usr/bin/env python3
# Praetorian H2020 Project
# Work Package 6	:	Response Coordination
# Task 4			:	Integration with Social Media
# ~~~~~~~~~~~~~~~~~~~~
# SMSTD-specific functionality

import string

tag_rules = 'lexicon_TD'
tag_identifiers = 'identifiers_TD'
tag_tweets = 'TD_tweets'
a = 0
b = 1

#############################
## CLASSIFICATION FUNCTION ##
#############################
def classifyTweet(tweet, identifiers, _, __):

	####################
	## INITIALIZATION ##
	####################
	classification = False
	priority = 'none'

	#####################
	## DATA EXTRACTION ##
	#####################
	# Get tweet text and location (if present)
	text = tweet['data']['text'].replace('Disclaimer: This tweet contains false information.', '')
	location = tweet['includes']['places'][0] if 'places' in tweet['includes'] else None

	#############
	## TAGGING ##
	#############
	# Surround words matching crawling rules with '$'
	already_tagged = []
	for rule in tweet['matching_rules']:
		for word in rule['tag'].split():
			if word != '&' and word not in already_tagged:
				text = text.replace(word, '$' + word + '$')
				already_tagged.append(word)

	# Clean up text and put it in a list
	clean_text_list = text.casefold().translate(str.maketrans('', '', string.punctuation)).split()

	####################
	## CLASSIFICATION ##
	####################
	# Check text for identifiers, surround words matching identifiers with '&'
	ids = []
	for identifier in identifiers:
		if identifier['value'].casefold() in clean_text_list:
			text = text.replace(identifier['value'], '&' + identifier['value'] + '&')
			ids.append(identifier['value'])
			classification = True
			priority = identifier['priority']

	# Check location for identifiers
	if location:
		location_stringified = (' '.join(list(location.values()))).casefold()
		if any(identifier['value'].casefold() in location_stringified for identifier in identifiers):
			ids.append(identifier['value'])
			classification = True
			priority = identifier['priority']

	return(classification, priority, text, ids)
