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
import os, datetime, time, sys, logging, random 

from flask import Flask, render_template, request, jsonify, g, make_response, has_request_context
from flask.logging import default_handler
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Summary, Counter, Histogram
from datetime import datetime
from logging.config import dictConfig
from prometheus_flask_exporter.multiprocess import UWsgiPrometheusMetrics

# Customize Logging Formats to Capture IP
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s '
    '%(levelname)s: %(message)s'
)
default_handler.setFormatter(formatter)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(remote_addr)s requested %(url)s '
    '%(levelname)s in %(module)s: %(message)s',
    }},
    'root': {
        'level': 'INFO',
    }
})

# Create app
app = Flask(__name__)
metrics = UWsgiPrometheusMetrics(app)
metrics.register_endpoint('/metrics')

@app.route("/")
def index():
    greeting = "Hello World!"
    app.logger.info("Successful Request")
    response = make_response(
                jsonify(
                    {"message": greeting, "severity": "info", "timestamp": datetime.now()}
                ),
                200,
    )
    return response

@app.route("/long")
def longroute():
    time.sleep(random.uniform(0.1,2.9))
    app.logger.info("Successful Long Request")
    return jsonify(message="This was a longer request!", request_time=datetime.now() )


@app.route("/badend")
def badend():
    1/0
    return '...'

@app.errorhandler(500)
def page_not_found(e):
    # specific 500 error to catch all missing pages
    app.logger.critical("500 Exception something is wrong here")
    return 'Hit an issue', 500

@app.errorhandler(404)
def page_not_found(e):
    # specific 404 error to catch all missing pages
    app.logger.error(f"404 Error page not found {request.url}")
    return jsonify(message="404 Error page not found", request_time=datetime.now() ), 404


if __name__ == '__main__':
    metrics.start_http_server(9100)
    app.run(debug=False, port=5000)