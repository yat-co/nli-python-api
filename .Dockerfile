FROM tiangolo/uwsgi-nginx-flask:python3.8

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG github_user
ARG github_key

RUN pip3 install git+https://$github_user:$github_key@github.com/yat-co/nli-python.git --upgrade

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app