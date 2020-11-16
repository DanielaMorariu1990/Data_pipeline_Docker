FROM python:3.6-slim 
#download debian &python
WORKDIR /app
#mkdir and cd to app

ADD requirements.txt /app 
# add all files to the directory
RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python","etl_analysis.py"]
# open bash 