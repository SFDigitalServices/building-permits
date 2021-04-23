"""Main application module"""
import os
import json
import jsend
import sentry_sdk
import falcon
from service.resources.welcome import Welcome
from service.resources.applications import Applications
from service.resources.application import Application
from service.resources.webhooks.bluebeam import BluebeamWebhook

def start_service():
    """Start this service
    set SENTRY_DSN environmental variable to enable logging with Sentry
    """
    # Initialize Sentry
    sentry_sdk.init(os.environ.get('SENTRY_DSN'))
    # Initialize Falcon
    api = falcon.App()
    api.add_route('/welcome', Welcome())
    api.add_route('/applications', Applications())
    api.add_route('/applications/{submission_id}', Application())
    api.add_route('/addenda', Applications('addenda'))
    api.add_route('/addenda/{submission_id}', Application('addenda'))
    api.add_route('/webhooks/bluebeam', BluebeamWebhook())
    api.add_sink(default_error, '')
    return api

def default_error(_req, resp):
    """Handle default error"""
    resp.status = falcon.HTTP_404
    msg_error = jsend.error('404 - Not Found')

    sentry_sdk.capture_message(msg_error)
    resp.text = json.dumps(msg_error)
