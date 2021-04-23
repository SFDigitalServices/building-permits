"""defining celery beat task for background polling of bluebeam-microservice exports"""
# pylint: disable=too-many-locals,too-many-branches,too-many-statements

import os
import traceback
import requests
import celery
from kombu import serialization
from service.resources.applications import Applications
import celeryconfig

serialization.register_pickle()
serialization.enable_insecure_serializers()

# pylint: disable=invalid-name
celery_app = celery.Celery('bluebeam-exporter')
celery_app.config_from_object(celeryconfig)
# pylint: enable=invalid-name


@celery_app.task(name="tasks.scheduler", bind=True)
def scheduler(self):
    # pylint: disable=unused-argument
    """
        queries for building permit applications and
        schedules them to be exported to bluebeam
    """
    print("scheduler starting...")

    # check queued records
    try:
        building_permit_applications = Applications()
        applications_to_export = building_permit_applications.perform_query({
            'actionState': 'Queued for Bluebeam'
        })

        project_users = []
        users_str = os.environ.get("BLUEBEAM_USERS")
        if users_str:
            project_users = [{'email': email} for email in users_str.split(",")]

        for application in applications_to_export:
            try:
                params = {
                    '_id': application.get('_id'),
                    'building_permit_number': application['data'].get(
                        'buildingPermitApplicationNumber'),
                    'project_name': application['data'].get('projectAddress'),
                    'project_id': application['data'].get('bluebeamId'),
                    'files': get_files(application),
                    '_webhook': {
                        'url': "{0}/webhooks/bluebeam".format(
                            os.environ.get('APP_URL').rstrip('/')),
                        'api_key': os.environ.get('BLUEBEAM_CALLBACK_API_KEY'),
                        'params': {
                            'type': building_permit_applications.application_type,
                            'submission_id': application.get('_id')},
                        'users': project_users
                    }}
                submission_response = requests.post(
                    '{0}/submission'.format(
                        os.environ.get('BLUEBEAM_MICROSERVICE_URL').rstrip('/')),
                    headers={'x-apikey':os.environ.get('BLUEBEAM_MICROSERVICE_API_KEY')},
                    json=params
                )
                submission_response.raise_for_status()
            except requests.HTTPError as err:
                print("Error exporting to Bluebeam Microservice: {0} {1}".format(
                    err.response.status_code, err.response.text))
                print("Attempted with: {0}".format(params))

    except Exception as err:    # pylint: disable=broad-except
        print("Encountered error in scheduler: {0}".format(err))
        print(traceback.format_exc())
        raise err
    finally:
        print("scheduler finished.")

def get_files(submission_json):
    """ find the json files blob since in can be in several different places """
    upload_fields = [
        'addendaUploads',
        'optionalUploads',
        'requiredUploads',
        'uploads'
    ]
    uploads = []
    submission_data = submission_json.get('data')
    for field in upload_fields:
        field_value = submission_data.get(field)
        if field_value is not None and len(field_value) > 0:
            uploads += submission_data.get(field)

    return uploads
