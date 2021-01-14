"""Application module"""
#pylint: disable=too-few-public-methods
import json
import jsend
import requests
import falcon
from sqlalchemy.orm.attributes import flag_modified
from service.resources.base_application import BaseApplication
import service.resources.google_sheets as gsheets
from service.resources.db import create_session
from service.resources.db_models import SubmissionModel
from service.resources.error import generic_error_handler, http_error_handler
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
            resp.body = json.dumps(gsheets.row_to_json(self.worksheet_title, row))
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

        session = create_session()
        db_session = session()
        original_data = None
        try:
            request_body = _req.bounded_stream.read()
            request_params_json = json.loads(request_body)

            # retrieve the submission from db
            app = db_session.query(SubmissionModel).filter(
                SubmissionModel.formio_id == submission_id
                ).first()
            original_data = app.data.copy()

            data = gsheets.create_spreadsheets_json(self.worksheet_title)

            data['label_value_map'] = {}
            for param, val in request_params_json.items():
                # db
                app.data['data'][param] = val

                # spreadsheet
                if param in gsheets.COLUMN_MAP:
                    column = gsheets.COLUMN_MAP[param]
                    data['label_value_map'][column] = val

            if not bool(data['label_value_map']):
                raise ValueError("Missing valid query parameters")

            # call api to update spreadsheet
            response = requests.patch(
                url='{0}/rows/{1}'.format(gsheets.SPREADSHEETS_MICROSERVICE_URL, submission_id),
                headers=gsheets.get_request_headers(),
                json=data
            )
            response.raise_for_status()

            flag_modified(app, 'data')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(jsend.success())
        except Exception as err:    #pylint: disable=broad-except
            # undo db edits
            if original_data is not None:
                app.data = original_data

            resp = generic_error_handler(err, resp)
        finally:
            db_session.commit()
