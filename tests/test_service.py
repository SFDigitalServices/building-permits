# pylint: disable=redefined-outer-name
"""Tests for microservice"""
import json
from unittest.mock import patch, Mock
from falcon import testing
import requests
import jsend
import tests.mocks as mocks
import service.microservice

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
    # happy path
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.text = json.dumps(jsend.success({'row':[mocks.SINGLE_ROW]}))
        mock_post.return_value.status_code = 200

        response = client.simulate_post(
            '/applications',
            json=mocks.JSON_OBJ
        )

        assert response.status_code == 200

    # error in call to spreadsheets microservice
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_post.return_value.status_code = 500

        response = client.simulate_post(
            '/applications',
            json=mocks.JSON_OBJ
        )

        assert response.status_code == 500

    # addenda post
    with patch('service.resources.applications.requests.post') as mock_post:
        mock_post.return_value.text = json.dumps(jsend.success({'row':[mocks.SINGLE_ROW]}))
        mock_post.return_value.status_code = 200

        response = client.simulate_post(
            '/addenda',
            json=mocks.JSON_OBJ
        )

        assert response.status_code == 200

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
    # happy path
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.return_value.text = json.dumps(mocks.PATCH_RESPONSE)
        mock_patch.return_value.status_code = 200

        response = client.simulate_patch(
            '/applications/123',
            json={'actionState': 'Queued for Bluebeam'}
        )

        assert response.status_code == 200

    # invalid parameter
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.return_value.text = json.dumps(mocks.PATCH_RESPONSE)
        mock_patch.return_value.status_code = 200

        response = client.simulate_patch(
            '/applications/123',
            json={
                'owner': 'me'
            }
        )

        assert response.status_code == 400

    # error in call to spreadsheets microservice
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_response = Mock(status_code=404, text='not found')
        mock_response.json.return_value = 'not found'
        mock_patch.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        response = client.simulate_patch(
            '/applications/123',
            json={
                'actionState': 'Queued for Bluebeam'
            }
        )
        assert response.status_code == 404

    # some generic error
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.side_effect = Exception('some generic error')

        response = client.simulate_patch(
            '/applications/123',
            json={
                'actionState': 'Queued for Bluebeam'
            }
        )
        assert response.status_code == 500

    # addenda
    with patch('service.resources.application.requests.patch') as mock_patch:
        mock_patch.return_value.text = json.dumps(mocks.PATCH_RESPONSE)
        mock_patch.return_value.status_code = 200

        response = client.simulate_patch(
            '/addenda/123',
            json={'actionState': 'Queued for Bluebeam'}
        )

        assert response.status_code == 200

@patch('service.resources.applications.requests.patch')
def test_bluebeam_webhook_success(mock_data_update, mock_env_access_key, client):
    # pylint: disable=unused-argument
    """
        Test bluebeam webhook endpoint with success message
    """
    print("begin test_bluebeam_webhook_success")
    mock_data_update.return_value.status_code = 200
    response = client.simulate_post(
        '/webhooks/bluebeam',
        params={
            'type': 'buildingPermitApplication', # or addenda.  defined in base_application
            'submission_id': '00001'
        },
        json=mocks.BLUEBEAM_SUCCESS_CALLBACK_PAYLOAD
    )

    assert response.status_code == 200
    assert mock_data_update.called_once_with(
        submission_id='00001',
        params={
            'actionState': 'Done',
            'bluebeam_project_id': '1234ABCD'
        }
    )

@patch('service.resources.applications.requests.patch')
def test_bluebeam_webhook_error(mock_data_update, mock_env_access_key, client):
    # pylint: disable=unused-argument
    """
        Test bluebeam webhook endpoint with error message
    """
    print("begin test_bluebeam_webhook_error")
    mock_data_update.return_value.status_code = 200
    response = client.simulate_post(
        '/webhooks/bluebeam',
        params={
            'type': 'addenda',
            'submission_id': '007'
        },
        json=mocks.BLUEBEAM_ERROR_CALLBACK_PAYLOAD
    )

    assert response.status_code == 200
    assert mock_data_update.called_once_with(
        submission_id='007',
        params={
            'actionState': 'error',
            'message': "I'm sorry Dave, I'm afraid can't do that."
        }
    )

@patch('service.resources.applications.requests.patch')
def test_bluebeam_webhook_data_update_error(mock_data_update, mock_env_access_key, client):
    # pylint: disable=unused-argument
    """
        Test bluebeam webhook endpoint handling of error when updating data
    """
    print("begin test_bluebeam_webhook_data_update_error")
    mock_data_update.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError
    response = client.simulate_post(
        '/webhooks/bluebeam',
        params={
            'type': 'addenda',
            'submission_id': '007'
        },
        json=mocks.BLUEBEAM_ERROR_CALLBACK_PAYLOAD
    )

    assert response.status_code == 500
    assert mock_data_update.called_once_with(
        submission_id='007',
        params={
            'actionState': 'error',
            'message': "I'm sorry Dave, I'm afraid can't do that."
        }
    )
