import tweepy
import requests
import os
import time


class NMTBot:
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token,
                 access_token_secret,
                 tweets_file):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.tweets_file = tweets_file
        self.last_tweet_idx = None

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(auth)

        def create_tweet(self, tweets_file, api):
            '''update status
            1) read a line from the translation file
            2) find the next tweet to post
            3) post to the twitter api
            '''

            with open(tweets_file, 'r') as f:
                pass

