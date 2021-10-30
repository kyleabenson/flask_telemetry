
# Apache header:

#     Copyright 2021 Google LLC

#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at

#         https://www.apache.org/licenses/LICENSE-2.0

#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-alpine

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

#Install gcc for wheel building and python deps
RUN apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers; 
RUN pip install -r requirements.txt; 
RUN apk del .build-deps;



#Add dir for multiprocessing mode
ENV PROMETHEUS_MULTIPROC_DIR /tmp
ENV prometheus_multiproc_dir /tmp
# Setup uWSGI
CMD uwsgi --http :$PORT --wsgi-file myapp.py --callable app