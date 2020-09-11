# pylint: disable=redefined-outer-name
"""Tests for google_sheets module"""

# import pprint
from unittest.mock import patch
import copy
import pytest
import mocks
import service.resources.google_sheets as gsheets

def test_create_spreadsheets_json():
    """Test create_spreadsheets_json function"""
    obj = gsheets.create_spreadsheets_json('worksheet_title')
    assert bool(obj)

    # missing worksheet_title
    with pytest.raises(ValueError):
        obj = gsheets.create_spreadsheets_json()


def test_row_to_json():
    """Test row_to_json function"""

    # for building permit applications
    obj = gsheets.row_to_json(gsheets.BUILDING_PERMIT_APPLICATION_WORKSHEET, mocks.SINGLE_ROW)
    # print("obj")
    # pprint.pprint(obj)
    assert obj == mocks.JSON_OBJ

    # for addenda
    obj = gsheets.row_to_json(gsheets.ADDENDA_APPLICATION_WORKSHEET, mocks.SINGLE_ROW_ADDENDA)
    assert obj == mocks.JSON_OBJ_ADDENDA

def test_json_to_row():
    """Test json_to_row function"""

    # for building permit applications
    row = gsheets.json_to_row(gsheets.BUILDING_PERMIT_APPLICATION_WORKSHEET, mocks.JSON_OBJ)
    # print("row")
    # pprint.pprint(row)
    assert row == mocks.SINGLE_ROW

    # addenda
    row = gsheets.json_to_row(gsheets.ADDENDA_APPLICATION_WORKSHEET, mocks.JSON_OBJ_ADDENDA)
    # print("*****")
    # print("row: {0}".format(row))
    # print("*****")
    # print("row: {0}".format(mocks.SINGLE_ROW_ADDENDA))
    assert row == mocks.SINGLE_ROW_ADDENDA

    # map _id path is wrong
    with patch('service.resources.google_sheets.get_map') as mock_get_map:
        mock_get_map.return_value = [{'path':['foo', '_id']}]
        row = gsheets.json_to_row(gsheets.BUILDING_PERMIT_APPLICATION_WORKSHEET, mocks.JSON_OBJ)
        assert row == [None]

def test_get_empty_string():
    """Test get_empty_string function"""
    assert gsheets.get_empty_string(mocks.JSON_OBJ) == ""

def test_get_locations():
    """Test get_location_values function"""

    # existing building location
    existing_building_obj = copy.deepcopy(mocks.JSON_OBJ)
    location1, location2 = gsheets.get_location_values(existing_building_obj)
    assert location1 == existing_building_obj['data']['existingBuildingAddress1']
    assert location2 == existing_building_obj['data']['existingBuildingAddress2']

    # new construction location
    new_construction_obj = copy.deepcopy(mocks.JSON_OBJ)
    new_construction_obj['data']['permitType'] = 'newConstruction'
    location1, location2 = gsheets.get_location_values(new_construction_obj)
    assert location1 == new_construction_obj['data']['newBuildingLocation']
    assert location2 is None

    # existing permit location
    existing_permit_obj = copy.deepcopy(mocks.JSON_OBJ)
    existing_permit_obj['data']['permitType'] = 'existingPermitApplication'
    location1, location2 = gsheets.get_location_values(existing_permit_obj)
    assert location1 == existing_permit_obj['data']['existingProjectAddress1']
    assert location2 == existing_permit_obj['data']['existingProjectAddress2']
