""" tests for celery tasks """
from unittest.mock import patch, Mock
import requests
import tests.mocks as mocks
from tasks import scheduler

@patch('tasks.requests.post')
@patch('service.resources.applications.requests.get')
def test_scheduler(mock_query_get, mock_bluebeam_post, mock_env_access_key):
    # pylint: disable=unused-argument
    """ Test the scheduler chron process """
    print("begin test_scheduler")

    mock_query_get.return_value.json.return_value = [mocks.SINGLE_ROW, mocks.SINGLE_ROW]
    scheduler.s().apply()

    assert mock_bluebeam_post.call_count == 2

@patch('tasks.requests.post')
@patch('service.resources.applications.requests.get')
def test_scheduler_bluebeam_error(mock_query_get, mock_bluebeam_post, mock_env_access_key):
    # pylint: disable=unused-argument
    """ Test the scheduler chron process """
    print("begin test_scheduler_bluebeam_error")

    mock_query_get.return_value.json.return_value = [mocks.SINGLE_ROW, mocks.SINGLE_ROW]
    mock_bluebeam_post.return_value.status_code = 500
    mock_response = Mock(status_code=500, text='Danger, Will Robinson!')
    mock_bluebeam_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )
    scheduler.s().apply()

    assert mock_bluebeam_post.call_count == 2
    assert mock_query_get.call_count == 1

@patch('tasks.requests.post')
@patch('service.resources.applications.requests.get')
def test_scheduler_query_error(mock_query_get, mock_bluebeam_post, mock_env_access_key):
    # pylint: disable=unused-argument
    """ Test the scheduler chron process """
    print("begin test_scheduler_query_error")

    mock_query_get.side_effect = Exception("Oops!")
    scheduler.s().apply()

    assert mock_bluebeam_post.call_count == 0
    assert mock_query_get.call_count == 1
