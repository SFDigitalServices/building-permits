"""Applcations module"""
#pylint: disable=too-few-public-methods
import json
import requests
import falcon
from service.resources.base_application import BaseApplication
import service.resources.google_sheets as gsheets
from service.resources.error import generic_error_handler, http_error_handler, value_error_handler
from .hooks import validate_access


@falcon.before(validate_access)
class Applications(BaseApplication):
    """Application class"""
    def on_post(self, _req, resp):
        #pylint: disable=no-self-use
        """
            creates a new application
        """
        try:
            submission_json = json.loads(_req.bounded_stream.read())
            data = gsheets.create_spreadsheets_json(self.worksheet_title)

            data["row_values"] = [gsheets.json_to_row(submission_json)]

            response = requests.post(
                url='{0}/rows'.format(gsheets.SPREADSHEETS_MICROSERVICE_URL),
                headers=gsheets.get_request_headers(),
                json=data
            )

            response.raise_for_status()

            resp.status = falcon.HTTP_200
            resp.body = response.text
        except Exception as err:    #pylint: disable=broad-except
            resp = generic_error_handler(err, resp)

    def on_get(self, _req, resp):
        #pylint: disable=no-self-use, duplicate-code
        """
            query for applications
        """
        try:
            data = gsheets.create_spreadsheets_json(self.worksheet_title)

            for param, val in _req.params.items():
                if param in gsheets.COLUMN_MAP:
                    data['column_label'] = param
                    data['value'] = val
                    break   #only query on one parameter at the moment

            if 'column_label' not in data:
                raise ValueError("Missing valid query parameters")

            response = requests.get(
                url='{0}/rows'.format(gsheets.SPREADSHEETS_MICROSERVICE_URL),
                headers=gsheets.get_request_headers(),
                params=data
            )

            response.raise_for_status()

            resp.status = falcon.HTTP_200
            resp.body = response.text

        except requests.HTTPError as err:
            resp = http_error_handler(err, resp)
        except ValueError as err:
            resp = value_error_handler(err, resp)
        except Exception as err:    #pylint: disable=broad-except
            resp = generic_error_handler(err, resp)
