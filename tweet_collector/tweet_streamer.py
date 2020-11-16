'''
Stream tweets using tweepy
'''
import os
import json
import logging
import os
import pymongo

from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

import config
import time


def authenticate():
    auth = OAuthHandler(config.CONSUMER_API_KEY,
                        config.CONSUMER_API_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN,
                          config.ACCESS_TOKEN_SECRET)

    return auth


class TwitterListener(StreamListener):

    def on_data(self, data):

        t = json.loads(data)  # t is just a regular python dictionary.

        tweet = {
            'text': t['text'],
            'username': t['user']['screen_name'],
            'followers_count': t['user']['followers_count'],
            'favorite_count': t['favorite_count'],
            'time_created': t['created_at']
        }

        logging.critical(f'\n\n\nTWEET INCOMING: {tweet["text"]}\n\n\n')
        collection.insert_one(tweet)
        logging.critical('end insert')

    def on_error(self, status):

        if status == 420:
            print(status)
            return False


if __name__ == '__main__':
    time.sleep(10)  # waiting for mongoDB to initiate
    client = pymongo.MongoClient('mongo_container')
    db = client.my_test
# create/use a collection
    collection = db.tweets
    auth = authenticate()
    listener = TwitterListener()
    stream = Stream(auth, listener)
    # stream.filter(follow=['@kjam'], languages=['en'])
    stream.filter(track=['Joe Biden', 'uselection',
                         'USElection'], languages=['en'])
