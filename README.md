# Docker-Compose project : building a slackbot from tweets

This project was cretaed during Spice Academy courses.

Below the arhitecture of the pipeline.

<img src="https://github.com/DanielaMorariu1990/Data_pipeline_Docker/blob/main/pipeline.PNG" width="700" height="350">

Is composed of 5 containers:

1. Tweet collector: collects tweets and stores them in MongoDB. Uses Tweeter APIs, tweepy and pymongo.

2. ETL: Reads tweets from MongoDB, cleanes data and calcules compound
   sentiment score (using Vader) and stores the outcome in PSQL, suing sqlAlchemy.

3. Slack bot: Slacks the most positives tweets on a defined Slack channel.

4. MongoDB container

5. PSQL container

## How to run?

1. Create Tweeter API and add them to a file called config.py
2. Create webhook for slack channel and that to conifg3.py (this part is optional, program can run without the slack_bot_1 container as well)
3. Run command 'Docker build' from main dir (where docker-compose file is), in order to build the image for the first time.
4. Run command 'Docker-compose up' to start all containers in yml file.
