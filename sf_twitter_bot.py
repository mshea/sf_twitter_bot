# The Sly Flourish Robot
#
# This Twitter robot posts a random #dnd tweet around 1pm every day from a
# database of previous D&D tweets I've posted to Sly Flourish.
# On Monday and Thursday at 2pm it posts a random Sly Flourish article
# from the article archives.
#
# I don't intend for this script to be used as-is for anything other
# than powering http://twitter.com/dndtweets. It will not run for you as-is.
# I'm simply posting this so others can learn from it, steal what works,
# and use it for their own evil twitter purposes.
#
# This script uses the tweepy library for Python to handle
# Twitter authentication. It also uses BeautifulSoup to handle HTML processing
#
# Updated 9 May 2013

import tweepy
import sqlite3
import time
import glob
import BeautifulSoup
import random

# Insert your Twitter API information here.
auth = tweepy.auth.OAuthHandler('yourapikeyhere',
		'yourapikeyhere')

auth.set_access_token('yourapikeyhere',
		'yourapikeyhere')

# This is the database this robot uses to post tweets.
tip_db = '/path/to/your/db.sqlite'

# These are words we don't want to include in our HTML reposts.
filename_badwords = ['index','dm_tips','rchive']

# We only retweet tweets that include these words.
tweet_whitelist = ['dnd','DnD','D&D','ungeon','ragon','izard','athfinder',
	'rpg','RPG']

# This is the directory where we look for HTML files to repost.
html_file_dir = '/path/to/your/html_files/'

# This is the base URL for our website.
html_url = 'http://yoururl.com/'

def score_and_retweet(auth):
	api = tweepy.API(auth)
	tweets = filter(tweet_filter, api.home_timeline(count=100, include_rts=0))
	for tweet in tweets:
		try:
			api.retweet(tweet.id_str)
		except tweepy.error.TweepError:
			error_id = tweet.id_str

def tweet_tip(tip_db, auth):
	t = time.localtime()
	if t.tm_hour is 13:
		conn = sqlite3.connect(tip_db)
		c = conn.cursor()
		random_tweet = c.execute('''
				select tweet
				from tweets
				where tweet like '%#dnd tip: %'
				order by random()
				limit 1;
				''')
		api = tweepy.API(auth)
		for tweet in random_tweet:
			tweet = BeautifulSoup.BeautifulSoup(tweet[0],
					convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES)
			api.update_status(tweet)

def find_and_tweet_article():
	t = time.localtime()
	# Post new articles around 2pm on Monday and Thursday.
	if t.tm_hour is 14 and (t.tm_wday is 1 or t.tm_wday is 4):
		htmlfiles = glob.glob(html_file_dir+'/*.html')
		filtered_files = filter(filename_filter, htmlfiles)
		chosen_file = random.choice(filtered_files)
		chosen_url = chosen_file.replace(html_file_dir,html_url)
		chosen_title = BeautifulSoup.BeautifulSoup(
				open(chosen_file).read()).title.string
		tweet = 'From the Sly Flourish Archive: '+chosen_title+' '\
				+ chosen_url + ' #dnd'
		api = tweepy.API(auth)
		api.update_status(tweet)

def filename_filter(f):
	for badword in filename_badwords:
		if badword in f: return False
	return True

def tweet_filter(t):
	# Include tweets that have a whitelisted word in them and >= 3 retweets
	for goodword in tweet_whitelist:
		if goodword in t.text and t.retweet_count >= 3: return True
	return False

def main(auth):
	score_and_retweet(auth)
	tweet_tip(tip_db, auth)
	find_and_tweet_article()

if __name__ == "__main__":
	main(auth)