"""
Selects the most postive tweets and slacks them in a predefined Slack channel
"""
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import requests
import time
import config3

time.sleep(30)

webhook_url = config3.webhook_url


engine = create_engine(
    'postgres://postgres:1234@pg_container:5432/postgres')

while True:
    select_query = """
    SELECT * FROM tweets_sentiment_1
    WHERE sentiment='positive'
    ORDER BY CREATED DESC
    LIMIT 4;
    """

    res = engine.execute(select_query)
    for row in res:
        post = {"text": (row["text"]), "sentiment_score": (
            str(row["sentiment_score"]))}
        requests.post(url=webhook_url, json=post)

    time.sleep(10)
