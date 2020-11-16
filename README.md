# Docker-Compose project : building a slackbot from tweets

Is composed of 5 containers:
\*Tweet collector: collects tweets and stores them in MOngoDB

\*ETL: Reads tweets from MongoDB, cleanes data and calcules compound
sentiment score (using Vader) and stores the outcome in PSQL

\*Slack bot: Slacks the most positives tweets on a defined Slack channel

\*MongoDB container

\*PSQL container
