"""Application module"""
#pylint: disable=too-few-public-methods
import json
import requests
import falcon
from service.resources.base_application import BaseApplication
import service.resources.google_sheets as gsheets
from service.resources.error import generic_error_handler, http_error_handler, value_error_handler
from .hooks import validate_access

@falcon.before(validate_access)
class Application(BaseApplication):
    """Application class"""

    def on_get(self, _req, resp, submission_id):
        #pylint: disable=no-self-use
        """
            retrieves an application by id
        """
        print("Application.on_get")
        try:
            data = gsheets.create_spreadsheets_json(self.worksheet_title)

            response = requests.get(
                url='{0}/rows/{1}'.format(gsheets.SPREADSHEETS_MICROSERVICE_URL, submission_id),
                headers=gsheets.get_request_headers(),
                params=data
            )

            response.raise_for_status()

            row = response.json()
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(gsheets.row_to_json(row))
        except requests.HTTPError as err:
            resp = http_error_handler(err, resp)
        except Exception as err:    #pylint: disable=broad-except
            resp = generic_error_handler(err, resp)

    def on_patch(self, _req, resp, submission_id):
        #pylint: disable=no-self-use, duplicate-code
        """
            update action state of an application
        """
        print("Application.on_patch")
        try:
            request_body = _req.bounded_stream.read()
            request_params_json = json.loads(request_body)

            data = gsheets.create_spreadsheets_json(self.worksheet_title)

            data['label_value_map'] = {}
            for param, val in request_params_json.items():
                if param in gsheets.COLUMN_MAP:
                    column = gsheets.COLUMN_MAP[param]
                    data['label_value_map'][column] = val

            if not bool(data['label_value_map']):
                raise ValueError("Missing valid query parameters")

            response = requests.patch(
                url='{0}/row/{1}'.format(gsheets.SPREADSHEETS_MICROSERVICE_URL, submission_id),
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
