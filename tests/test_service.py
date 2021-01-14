# pylint: disable=redefined-outer-name
"""Tests for microservice"""
import json
from unittest.mock import patch, Mock
import pytest
from falcon import testing
import requests
import jsend
import mocks
from service.resources.db import create_session
from service.resources.db_models import SubmissionModel
import service.microservice


CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

session = create_session() # pylint: disable=invalid-name
db_session = session() # pylint: disable=invalid-name

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])

@pytest.fixture
def mock_env_no_access_key(monkeypatch):
    """ mock environment with no access key """
    monkeypatch.delenv("ACCESS_KEY", raising=False)

def clear_submissions():
    """ clear out submission table """
    print("clearing out all submissions in the db...")
    db_session.query(SubmissionModel).delete()
    db_session.commit()

def test_welcome(client, mock_env_access_key):
    # pylint: disable=unused-argument
    # mock_env_access_key is a fixture and creates a false positive for pylint
    """Test welcome message response"""
    response = client.simulate_get('/welcome')
    assert response.status_code == 200

    expected_msg = jsend.success({'message': 'Welcome'})
    assert json.loads(response.content) == expected_msg

    # Test welcome request with no ACCESS_KEY in header
    client_no_access_key = testing.TestClient(service.microservice.start_service())
    response = client_no_access_key.simulate_get('/welcome')
    assert response.status_code == 403

def test_welcome_no_access_key(client, mock_env_no_access_key):
    # pylint: disable=unused-argument
    # mock_env_no_access_key is a fixture and creates a false positive for pylint
    """Test welcome request with no ACCESS_key environment var set"""
    response = client.simulate_get('/welcome')
    assert response.status_code == 403

def test_default_error(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """Test default error response"""
    response = client.simulate_get('/some_page_that_does_not_exist')

    assert response.status_code == 404

    expected_msg_error = jsend.error('404 - Not Found')
    assert json.loads(response.content) == expected_msg_error

def test_applications_post(mock_env_access_key, client):
    # pylint: disable=unused-argument
    """
        Test creation of new application
    """
    clear_submissions()

    # happy path
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.text = json.dumps(jsend.success({'row':[mocks.SINGLE_ROW]}))
        mock_post.return_value.status_code = 200

        response = client.simulate_post(
            '/applications',
            json=mocks.JSON_OBJ
        )

        assert response.status_code == 200

    # db unique id error
    # happy path
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.text = json.dumps(jsend.success({'row':[mocks.SINGLE_ROW]}))
        mock_post.return_value.status_code = 200

        response = client.simulate_post(
            '/applications',
            json=mocks.JSON_OBJ
        )

        assert response.status_code == 500

    # error in call to spreadsheets microservice
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_post.return_value.status_code = 500

        params = mocks.JSON_OBJ.copy()
        params["_id"] = "permit2"
        response = client.simulate_post(
            '/applications',
            json=params
        )

        assert response.status_code == 500
        # check that no new submission added to db
        submissions = db_session.query(SubmissionModel)
        assert submissions.count() == 1

    # addenda post
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.text = json.dumps(jsend.success({'row':[mocks.SINGLE_ROW_ADDENDA]}))
        mock_post.return_value.status_code = 200

        response = client.simulate_post(
            '/addenda',
            json=mocks.JSON_OBJ_ADDENDA
        )

        assert response.status_code == 200

    # missing formio.id
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.text = json.dumps(jsend.success({'row':[mocks.SINGLE_ROW]}))
        mock_post.return_value.status_code = 200

        submission_mock = mocks.JSON_OBJ.copy()
        del submission_mock['_id']

        response = client.simulate_post(
            '/applications',
            json=submission_mock
        )

        assert response.status_code == 500
        # check that no new submission added to db
        submissions = db_session.query(SubmissionModel)
        assert submissions.count() == 2

def test_applications_get(mock_env_access_key, client):
    # pylint: disable=unused-argument
    """
        test query endpoint
    """
    # happy path
    with patch('service.resources.applications.requests.get') as mock_get:
        mock_get.return_value.json.return_value = [mocks.SINGLE_ROW, mocks.SINGLE_ROW]
        mock_get.return_value.status_code = 200

        response = client.simulate_get(
            '/applications',
            params={
                'actionState': 'Queued for Bluebeam'
            }
        )

        assert response.status_code == 200
        response_json = json.loads(response.text)
        assert isinstance(response_json, list)
        assert len(response_json) == 2

    # missing valid query parameter
    with patch('service.resources.applications.requests.get') as mock_get:
        mock_get.return_value.text = json.dumps([mocks.SINGLE_ROW, mocks.SINGLE_ROW])
        mock_get.return_value.status_code = 200

        response = client.simulate_get(
            '/applications',
            params={
                'admin': 'me'
            }
        )

        assert response.status_code == 400

    # error in spreadsheets api call
    with patch('service.resources.applications.requests.get') as mock_get:
        mock_response = Mock(status_code=404, text='not found')
        mock_response.json.return_value = 'not found'
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        response = client.simulate_get(
            '/applications',
            params={
                'actionState': 'Queued for Bluebeam'
            }
        )

        assert response.status_code == 404

    # some generic error
    with patch('service.resources.applications.requests.get') as mock_get:
        mock_get.side_effect = Exception('some generic error')

        response = client.simulate_get(
            '/applications',
            params={
                'actionState': 'Queued for Bluebeam'
            }
        )

        assert response.status_code == 500

    # addenda
    with patch('service.resources.applications.requests.get') as mock_get:
        mock_get.return_value.text = json.dumps([mocks.SINGLE_ROW, mocks.SINGLE_ROW])
        mock_get.return_value.status_code = 200

        response = client.simulate_get(
            '/addenda',
            params={
                'actionState': 'Queued for Bluebeam'
            }
        )

        assert response.status_code == 200

def test_application_get(mock_env_access_key, client):
    # pylint: disable=unused-argument
    """
        Test retrieval of an application
    """
    # happy path
    with patch('service.resources.application.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mocks.SINGLE_ROW
        mock_get.return_value.status_code = 200

        response = client.simulate_get('/applications/123')

        assert response.status_code == 200
        response_json = json.loads(response.text)
        assert response_json == mocks.JSON_OBJ

    # error in call to spreadsheets microservice
    with patch('service.resources.application.requests.get') as mock_get:
        mock_response = Mock(status_code=404, text='not found')
        mock_response.json.return_value = 'not found'
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        response = client.simulate_get('/applications/456')
        assert response.status_code == 404

    # some generic error
    with patch('service.resources.application.requests.get') as mock_get:
        mock_get.side_effect = Exception('some generic error')

        response = client.simulate_get('/applications/789')
        assert response.status_code == 500

    # addenda
    with patch('service.resources.application.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mocks.SINGLE_ROW_ADDENDA
        mock_get.return_value.status_code = 200

        response = client.simulate_get('/addenda/123')
        assert response.status_code == 200

def test_application_patch(mock_env_access_key, client):
    # pylint: disable=unused-argument
    """
        Test updating an application
    """
    formio_id = '5f19eb423339194c18c45c7a'
    queued_for_bluebeam = 'Queued for Bluebeam'
    # happy path
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.return_value.text = json.dumps(mocks.PATCH_RESPONSE)
        mock_patch.return_value.status_code = 200

        response = client.simulate_patch(
            '/applications/{0}'.format(formio_id),
            json={'actionState': queued_for_bluebeam}
        )

        assert response.status_code == 200
        submission = db_session.query(SubmissionModel).filter(
            SubmissionModel.formio_id == formio_id
        ).one()
        assert submission.data['data']['actionState'] == queued_for_bluebeam

    # invalid parameter
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.return_value.text = json.dumps(mocks.PATCH_RESPONSE)
        mock_patch.return_value.status_code = 200

        response = client.simulate_patch(
            '/applications/{0}'.format(formio_id),
            json={
                'ownerName': 'me'
            }
        )

        assert response.status_code == 500
        submission = db_session.query(SubmissionModel).filter(
            SubmissionModel.formio_id == formio_id
        ).one()
        assert submission.data['data']['ownerName'] != 'me'

    # error in call to spreadsheets microservice
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_response = Mock(status_code=404, text='not found')
        mock_response.json.return_value = 'not found'
        mock_patch.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        response = client.simulate_patch(
            '/applications/{0}'.format(formio_id),
            json={
                'actionState': 'test'
            }
        )
        assert response.status_code == 500
        submission = db_session.query(SubmissionModel).filter(
            SubmissionModel.formio_id == formio_id
        ).one()
        assert submission.data['data']['actionState'] != 'test'

    # some generic error
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.side_effect = Exception('some generic error')

        response = client.simulate_patch(
            '/applications/{0}'.format(formio_id),
            json={
                'actionState': 'test'
            }
        )
        assert response.status_code == 500
        submission = db_session.query(SubmissionModel).filter(
            SubmissionModel.formio_id == formio_id
        ).one()
        assert submission.data['data']['actionState'] != 'test'

    # addenda
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.return_value.text = json.dumps(mocks.PATCH_RESPONSE)
        mock_patch.return_value.status_code = 200

        response = client.simulate_patch(
            '/addenda/5ed81beb463bc6df71e2500f',
            json={'actionState': queued_for_bluebeam}
        )

        assert response.status_code == 200
        submission = db_session.query(SubmissionModel).filter(
            SubmissionModel.formio_id == '5ed81beb463bc6df71e2500f'
        ).one()
        assert submission.data['data']['actionState'] == queued_for_bluebeam
