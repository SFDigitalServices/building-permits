"""Application module"""
#pylint: disable=too-few-public-methods
import json
import requests
import falcon
import service.resources.google_sheets as gsheets
from service.resources.error import generic_error_handler, http_error_handler
from .hooks import validate_access

@falcon.before(validate_access)
class Application():
    """Application class"""
    def on_get(self, _req, resp, submission_id):
        #pylint: disable=no-self-use
        """
            retrieves an application by id
        """
        print("Application.on_get")
        try:
            data = gsheets.create_spreadsheets_json()
            response = requests.get(
                url='{0}/rows/{1}'.format(gsheets.SPREADSHEETS_MICROSERVICE_URL, submission_id),
                headers={
                    'x-apikey': gsheets.SPREADSHEETS_MICROSERVICE_API_KEY
                },
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
