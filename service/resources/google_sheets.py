""" Methods for Google Sheets interaction """
#pylint: disable=too-few-public-methods
import os
import json

SPREADSHEETS_MICROSERVICE_URL = os.environ.get("SPREADSHEETS_MICROSERVICE_URL")
SPREADSHEETS_MICROSERVICE_API_KEY = os.environ.get("SPREADSHEETS_MICROSERVICE_API_KEY")
SPREADSHEET_KEY = os.environ.get("SPREADSHEET_KEY")
SPREADSHEETS_ID_COL = "A"
SPREADSHEETS_BLUEBEAM_ID_COL = "ES"
SPREADSHEETS_OPTIONAL_UPLOADS_COL = "ET"
SPREADSHEETS_REQUIRED_UPLOADS_COL = "EU"
SPREADSHEETS_PROJECT_LOCATION_ADDR1_COL = "FA"
SPREADSHEETS_PROJECT_LOCATION_ADDR2_COL = "FB"
SPREADSHEETS_FILES_JSON_COL = "FC"

BUCKETEER_PATH = os.environ.get("BUCKETEER_DOMAIN")
DS_PATH = os.environ.get("DS_PATH")

PROJECT_LOCATION_1 = "PROJECT_LOCATION_1"
PROJECT_LOCATION_2 = "PROJECT_LOCATION_2"
FILES_JSON_STRING = "FILES_JSON_STRING"

def get_request_headers():
    """
        headers for request to spreadsheets microservice
    """
    return {
        'x-apikey': SPREADSHEETS_MICROSERVICE_API_KEY
    }

def get_empty_string(submission_json):
    #pylint: disable=unused-argument
    """
        Empty String - For consistency in defining the map
    """
    return ""

def get_location1(submission_json):
    """
        wrapper for get_location_values but returns location1 only
    """
    return get_location_values(submission_json)[0]

def get_location2(submission_json):
    """
        wrapper for get_location_values but returns location2 only
    """
    return get_location_values(submission_json)[1]

def get_location_values(submission_json):
    """
        normalize project location values
    """
    permit_type = submission_json['data']['permitType']
    location1 = None
    location2 = None
    if permit_type == 'existingBuilding':
        location1 = submission_json['data']['existingBuildingAddress1']
        location2 = submission_json['data']['existingBuildingAddress2']
    elif permit_type == 'newConstruction':
        location1 = submission_json['data']['newBuildingLocation']
    elif permit_type == 'existingPermitApplication':
        location1 = submission_json['data']['existingProjectAddress1']
        location2 = submission_json['data']['existingProjectAddress2']
    return location1, location2

def get_files_links(submission_json):
    """
        consolidate all the file urls into one string
    """
    files = []
    upload_fields = [
        'addendaUploads',
        'optionalUploads',
        'requiredUploads',
        'uploads',
        'confirmationUploads'
    ]

    for field in upload_fields:
        if field in submission_json['data']:
            files = files + list(
                map(
                    lambda x: x.get('url').replace(BUCKETEER_PATH, DS_PATH),
                    submission_json['data'][field]
                )
            )

    return ",\n".join(files)

def create_spreadsheets_json(worksheet_title=None):
    """
        create base parameters json for spreadsheets api call
    """
    if worksheet_title is None:
        raise ValueError('Missing worksheet_title parameter')

    return {
        "spreadsheet_key": SPREADSHEET_KEY,
        "worksheet_title": worksheet_title,
        "id_column_label": SPREADSHEETS_ID_COL,
    }

COLUMN_MAP = {
    'actionState': 'B'
}

ROW_JSON_MAP = [
    {'path':['_id']},
    {'path':['data', 'actionState'], 'value':get_empty_string}, # action state
    {'path':['data', 'bluebeamStatus'], 'value':get_empty_string}, # Blubeam status
    {'path':['data', 'ptsStatus'], 'value':get_empty_string}, # pts status
    {'path':['created']},
    {'path':['modified']},
    {'path':['data', 'permitType']},
    {'path':['data', 'reviewOverTheCounter']},
    {'path':['data', 'onlyFireDepartmentReview']},
    {'path':['data', 'applicantType']},
    {'path':['data', 'applicantFirstName']},
    {'path':['data', 'applicantLastName']},
    {'path':['data', 'applicantPhoneNumber']},
    {'path':['data', 'applicantEmail']},
    {'path':['data', 'applicantAddress1']},
    {'path':['data', 'applicantAddress2']},
    {'path':['data', 'applicantCity']},
    {'path':['data', 'Page2State']},
    {'path':['data', 'applicantZipCode']},
    {'path':['data', 'applicantContractorLicenseNumber']},
    {'path':['data', 'applicantContractorLicenseExpirationDate']},
    {'path':['data', 'applicantBTRC']},
    {'path':['data', 'applicantArchitectLicenseNumber']},
    {'path':['data', 'applicantArchitectLicenseExpirationDate']},
    {'path':['data', 'applicantEngineerLicenseNumber']},
    {'path':['data', 'applicantEngineerLicenseExpirationDate']},
    {'path':['data', 'buildingPermitApplicationNumber']},
    {'path':['data', 'existingProjectAddress1']},
    {'path':['data', 'existingProjectAddress2']},
    {'path':['data', 'existingProjectZipCode']},
    {'path':['data', 'existingProjectDescribeApplicationChanges']},
    {'path':['data', 'ownerName']},
    {'path':['data', 'ownerPhoneNumber']},
    {'path':['data', 'ownerEmail']},
    {'path':['data', 'ownerAddress1']},
    {'path':['data', 'ownerAddress2']},
    {'path':['data', 'ownerCity']},
    {'path':['data', 'ownerState']},
    {'path':['data', 'ownerZipCode']},
    {'path':['data', 'teamMembers', 'agent']},
    {'path':['data', 'teamMembers', 'architect']},
    {'path':['data', 'teamMembers', 'attorneyInFact']},
    {'path':['data', 'teamMembers', 'contractor']},
    {'path':['data', 'teamMembers', 'engineer']},
    {'path':['data', 'agentOrganizationName']},
    {'path':['data', 'agentName']},
    {'path':['data', 'agentEmail']},
    {'path':['data', 'architectOrganizationName']},
    {'path':['data', 'architectName']},
    {'path':['data', 'architectEmail']},
    {'path':['data', 'architectLicenseNumber']},
    {'path':['data', 'architectLicenseExpirationDate']},
    {'path':['data', 'attorneyOrganizationName']},
    {'path':['data', 'attorneyName']},
    {'path':['data', 'attorneyEmail']},
    {'path':['data', 'contractorOrganizationName']},
    {'path':['data', 'contractorName']},
    {'path':['data', 'contractorEmail']},
    {'path':['data', 'contractorLicenseNumber']},
    {'path':['data', 'contractorLicenseExpirationDate']},
    {'path':['data', 'contractorBTRC']},
    {'path':['data', 'engineerOrganizationName']},
    {'path':['data', 'engineerName']},
    {'path':['data', 'engineerEmail']},
    {'path':['data', 'engineerLicenseNumber']},
    {'path':['data', 'engineerLicenseExpirationDate']},
    {'path':['data', 'newBuildingLocation']},
    {'path':['data', 'newBuildingBlockNumber']},
    {'path':['data', 'newBuildingLotNumber']},
    {'path':['data', 'newBuildingLotFront']},
    {'path':['data', 'newBuildingLotBack']},
    {'path':['data', 'newBuildingLotAverageDepth']},
    {'path':['data', 'newBuildingStreetFaced']},
    {'path':['data', 'newBuildingStreetSide']},
    {'path':['data', 'newBuildingNearestCrossStreet']},
    {'path':['data', 'newBuildingCrossStreetDirection']},
    {'path':['data', 'newBuildingCrossStreetDistance']},
    {'path':['data', 'newBuildingLotHasOtherBuilding']},
    {'path':['data', 'existingBuildingAddress1']},
    {'path':['data', 'existingBuildingAddress2']},
    {'path':['data', 'existingBuildingCity']},
    {'path':['data', 'existingBuildingState']},
    {'path':['data', 'existingBuildingZipCode']},
    {'path':['data', 'existingBuildingBlockNumber']},
    {'path':['data', 'existingBuildingLotNumber']},
    {'path':['data', 'existingBuildingConstructionType']},
    {'path':['data', 'existingBuildingDwellingUnits']},
    {'path':['data', 'existingBuildingOccupancyStories']},
    {'path':['data', 'existingBuildingBasementsAndCellars']},
    {'path':['data', 'existingBuildingPresentUse']},
    {'path':['data', 'existingBuildingOccupancyClass']},
    {'path':['data', 'sitePermitForm38']},
    {'path':['data', 'noticeOfViolation']},
    {'path':['data', 'estimatedCostOfProject']},
    {'path':['data', 'projectDescription']},
    {'path':['data', 'typeOfConstruction']},
    {'path':['data', 'proposedDwellingUnits']},
    {'path':['data', 'proposedOccupancyStories']},
    {'path':['data', 'proposedBasementsAndCellars']},
    {'path':['data', 'proposedUse']},
    {'path':['data', 'occupancyClass']},
    {'path':['data', 'constructionLenderName']},
    {'path':['data', 'constructionLenderBranchDesignation']},
    {'path':['data', 'constructionLenderAddress1']},
    {'path':['data', 'constructionLenderAddress2']},
    {'path':['data', 'constructionLenderCity']},
    {'path':['data', 'constructionLenderState']},
    {'path':['data', 'constructionLenderZipCode']},
    {'path':['data', 'sitePermitForm12']},
    {'path':['data', 'newEstimatedCostOfProject']},
    {'path':['data', 'newProjectDescription']},
    {'path':['data', 'newTypeOfConstruction']},
    {'path':['data', 'newBuildingUse']},
    {'path':['data', 'newOccupancyClass']},
    {'path':['data', 'newGroundFloorArea']},
    {'path':['data', 'newBuildingFrontHeight']},
    {'path':['data', 'newDwellingUnits']},
    {'path':['data', 'newOccupancyStories']},
    {'path':['data', 'newBasements']},
    {'path':['data', 'newConstructionLenderName']},
    {'path':['data', 'newConstructionLenderBranchDesignation']},
    {'path':['data', 'constructionLenderAddress3']},
    {'path':['data', 'constructionLenderAddress4']},
    {'path':['data', 'constructionLenderCity1']},
    {'path':['data', 'constructionLenderState1']},
    {'path':['data', 'constructionLenderZipCode1']},
    {'path':['data', 'alterOrConstructDriveway']},
    {'path':['data', 'useStreetSpace']},
    {'path':['data', 'electricalWork']},
    {'path':['data', 'plumbingWork']},
    {'path':['data', 'additionalHeightOrStory']},
    {'path':['data', 'newCenterLineFrontHeight']},
    {'path':['data', 'deckOrHorizontalExtension']},
    {'path':['data', 'groundFloorArea']},
    {'path':['data', 'repairOrAlterSidewalk']},
    {'path':['data', 'extendBeyondPropertyLine']},
    {'path':['data', 'otherExistingBuildings']},
    {'path':['data', 'changeOfOccupancy']},
    {'path':['data', 'alterOrConstructDrivewayNew']},
    {'path':['data', 'extendBeyondPropertyLineNew']},
    {'path':['data', 'useStreetSpaceNew']},
    {'path':['data', 'additionalStoriesNew']},
    {'path':['data', 'howManyAdditionalStoriesNew']},
    {'path':['data', 'useSidewalkSpaceNew']},
    {'path':['data', 'affordableHousing']},
    {'path':['data', 'developmentAgreement']},
    {'path':['data', 'accessoryDwellingUnit']},
    {'path':['data', 'uploadType']},
    {'path':['data', 'bluebeamId']},
    {'path':['data', 'optionalUploads']},
    {'path':['data', 'requiredUploads']},
    {'path':['data', 'noPlansPermit']},
    {'path':['data', 'notes']},
    {'path':['data', 'workersCompRadio']},
    {'path':['data', 'iHerebyCertifyCheckBox']},
    {'path':['data', 'dateTime']},
    {'path':['data', 'projectLocation1'], 'value':get_location1},
    {'path':['data', 'projectLocation2'], 'value':get_location2},
    {'path':['data', 'fileLinks'], 'value':get_files_links},
    {'path':['data', 'confirmationUploads']},
    {'path':['data', 'priorityProjectSelections', 'isInDevelopmentAgreement']},
    {'path':['data', 'priorityProjectSelections', 'is100AffordableHousing']}
]

def get_map():
    """
        return ROW_JSON_MAP
        for mocking purposes
    """
    return ROW_JSON_MAP

def json_to_row(submission_json):
    # pylint: disable=too-many-branches
    """
        create row array from json
    """
    row = []
    the_map = get_map()
    for mapped_item in the_map:
        if 'value' in mapped_item:
            row.append(mapped_item['value'](submission_json))
        else:
            path = mapped_item['path']

            # pull the value from submission json object
            val = submission_json
            last_prop = path[-1]

            for prop in path:
                val = val.get(prop)
                if val is None:
                    raise Exception(
                        "Mapping path element not found in submission json: {0}".format(path)
                    )

            if isinstance(val, list):
                if len(val) > 0:
                    first_item = val[0]

                    if "originalName" in first_item:
                        # file uploads
                        row.append(json.dumps(val))
                    elif "LotNumber" in last_prop:
                        # lot
                        row.append(",".join(val))
                    else:
                        # all other lists
                        row.append(",\n".join(val))
                else:
                    row.append("[]")
            else:
                row.append(val)

    return row

def row_to_json(row):
    """
        create json from row
    """
    obj = {}
    the_map = get_map()
    for idx, val in enumerate(row):
        path = the_map[idx]['path']
        last_path = path[-1]
        current_obj = obj

        # convert value to array?
        if "LotNumber" in last_path:
            val = val.split(",")
        elif "originalName" in val or val == "[]":
            val = json.loads(val)
        elif ",\n" in val:
            val = val.split(",\n")

        for path_item in path:
            if path_item == last_path:
                current_obj[path_item] = val
            elif path_item not in current_obj:
                current_obj[path_item] = {}
            current_obj = current_obj[path_item]
    return obj