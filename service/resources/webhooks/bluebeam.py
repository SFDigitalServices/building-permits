"""bluebeam webhook module"""
#pylint: disable=too-few-public-methods
import json
import traceback
import falcon
import jsend
from service.resources.application import Application
from service.resources.hooks import validate_access

@falcon.before(validate_access)
class BluebeamWebhook():
    """ Bluebeam Webhook class """

    def on_post(self, _req, resp):
        #pylint: disable=no-self-use,no-member,unused-argument
        """
            bluebeam webook
        """
        try:
            callback = _req.media
            application = Application(_req.get_param('type'))

            if jsend.is_success(callback):
                application.update(
                    _req.get_param('submission_id'),
                    {
                        'actionState': 'Done',
                        'bluebeamStatus': callback['data'].get('bluebeam_project_id')
                    })
            else:
                application.update(
                    _req.get_param('submission_id'),
                    {
                        'actionState': 'Error',
                        'bluebeamStatus': callback.get('message')
                    })

            resp.status = falcon.HTTP_200
        except Exception as err: # pylint: disable=broad-except
            error = "BluebeamWebhook.on_get ERROR: {0}".format(err)
            print(error)
            print(traceback.format_exc())
            resp.status = falcon.HTTP_500
            resp.text = json.dumps(jsend.error("error"))
