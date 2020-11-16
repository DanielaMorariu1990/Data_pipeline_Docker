
""""
Reading in Tweet data from MongoDB 
        -clenaing data
        -calculatig a compound sentiment score using Vader
        - writting new data to PSQL

"""
import pymongo
import re
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import psycopg2
import time
import os
import config2

# initiating logging file
logging.basicConfig(level=logging.INFO, filename='etl2.log',
                    format='%(asctime)s:%(levelname)s:%(message)s')

# initiating Vader sentiment analysis
analyizer = SentimentIntensityAnalyzer()

# clean tweeter data (extract RT and spaces and white lines etc)


def data_cleaning(data):
    data["text"] = data["text"].apply(lambda x: re.sub(r"RT @[\w]*:", "", x))
    data["text"] = data["text"].apply(lambda x: re.sub(r'@[\w]*', "", x))
    data["text"] = data["text"].apply(lambda x: re.sub(
        r'https?://[A-Za-z0-9./]*', "", x))
    data["text"] = data["text"].apply(lambda x: re.sub('\n', "", x))
    data["text"] = data["text"].apply(lambda x: x.replace("$", ""))
    data["text"] = data["text"].apply(lambda x: x.replace("%", ""))
    data["text"] = data["text"].apply(lambda x: x.replace("&", ""))
    data["text"] = data["text"].apply(lambda x: x.replace("*", ""))
    data["text"] = data["text"].apply(lambda x: x.replace("#", ""))
    data["text"] = data["text"].apply(lambda x: x.replace(":", ""))
    data["text"] = data["text"].apply(lambda x: x.replace("(", ""))
    data["text"] = data["text"].apply(lambda x: x.replace(")", ""))
    data["text"] = data["text"].apply(lambda x: x.replace(".", ""))

    return data

# calculate sentiment score (extract only the compund sentiment)


def model_vader(sentence, analyizer=analyizer):

    score = analyizer.polarity_scores(sentence)["compound"]
    return score


if __name__ == '__main__':
    # establishing database connections: MongoDB to read in and PSQL to write output
    # activate autocommit to be able to cretae tables
    # transform it to pandas data frame and apply cleaning and sentiment calculation
    time.sleep(5)  # waiting for mongoDB to initiate
    engine = create_engine(
        'postgres://postgres:1234@pg_container:5432/postgres')
    engine.raw_connection().set_isolation_level(
        psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    client = pymongo.MongoClient('mongo_container', port=27017)
    tweets = None

    while True:

        db = client.my_test
        collection = db.tweets
        old = tweets
        # reading in from MONGODB
        tweets = pd.DataFrame(
            list(collection.find()))

        if old is not None:
            df = pd.concat([old, tweets])
            df.drop_duplicates(keep=False, inplace=True)
            tweets = df

        logging.info('Inspecting data type : ' + str(type(tweets["text"])))

        # clean data
        tweets = data_cleaning(tweets)

        # calculate sentiment
        tweets["sentiment_score"] = tweets["text"].apply(
            lambda x: model_vader(x))

        logging.info(
            f"Insepcting sentiment outcome {tweets['sentiment_score'].iloc[:3]}")

        # classifying sentiment
        tweets["sentiment"] = tweets["sentiment_score"].apply(lambda x: "positive" if x > 0.05
                                                              else ("negative" if x < -0.05 else
                                                                    "neutral"))
        logging.warning(f"Inspecting sentiment:{tweets['sentiment'].iloc[:3]}")

        # transforming to date time for inserting into data base

        create_table = """
        CREATE TABLE IF NOT EXISTS tweets_sentiment_1(
        USERNAME VARCHAR(100),
        TEXT VARCHAR(500),
        FOLLOWERS NUMERIC,
        CREATED DATE,
        FAVORITES NUMERIC,
        SENTIMENT_SCORE NUMERIC,
        SENTIMENT VARCHAR(100)
        );
        """
        engine.execute(create_table)

        for i in range(tweets.iloc[:2].shape[0]):
            logging.info(
                f"""INSERT INTO tweets_sentiment_1 VALUES
                ('{tweets['username'].iloc[i]}',
                $${tweets['text'].iloc[i]}$$,
                {tweets['followers_count'].iloc[i]},
                '{tweets['time_created'].iloc[i]}',
                {tweets['favorite_count'].iloc[i]},
                {tweets['sentiment_score'].iloc[i]},
                '{tweets['sentiment'].iloc[i]}'); """)

        tweets.drop_duplicates(subset=["text"], inplace=True)

        # insert outcome into PSQL table
        for i in range(tweets.shape[0]):
            logging.critical("INSERTING INTO PSQL BEGIN")
            insert_query = f"""INSERT INTO tweets_sentiment_1 VALUES
                ('{tweets['username'].iloc[i]}',
                $${tweets["text"].iloc[i]}$$,
                {tweets['followers_count'].iloc[i]},
                '{tweets['time_created'].iloc[i]}',
                {tweets['favorite_count'].iloc[i]},
                {tweets['sentiment_score'].iloc[i]},
                '{tweets['sentiment'].iloc[i]}'); """
            engine.execute(sqlalchemy.text(insert_query))
            logging.critical(sqlalchemy.text(insert_query))
            logging.critical("INSERTING INTO PSQL END")
