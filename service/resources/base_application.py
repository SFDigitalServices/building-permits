"""base application module"""

import service.resources.google_sheets as gsheets

class BaseApplication():
    """ BaseApplication Class """
    # pylint: disable=too-few-public-methods

    def __init__(self, application_type='buildingPermitApplication'):
        if application_type == 'addenda':
            self.worksheet_title = gsheets.ADDENDA_APPLICATION_WORKSHEET
        else:
            self.worksheet_title = gsheets.BUILDING_PERMIT_APPLICATION_WORKSHEET
