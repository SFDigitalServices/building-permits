""" shared fixtures """
import pytest
from falcon import testing
import service.microservice


CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])
    monkeypatch.setenv("APP_URL", "APP_URL")
    monkeypatch.setenv("BLUEBEAM_CALLBACK_API_KEY", "BLUEBEAM_CALLBACK_API_KEY")
    monkeypatch.setenv("BLUEBEAM_MICROSERVICE_API_KEY", "BLUEBEAM_MICROSERVICE_API_KEY")
    monkeypatch.setenv("BLUEBEAM_MICROSERVICE_URL", "BLUEBEAM_MICROSERVICE_URL")
    monkeypatch.setenv("BLUEBEAM_USERS", "a@email.com,b@email.com")
    monkeypatch.setenv("BUILDING_PERMITS_API_KEY", "BUILDING_PERMITS_API_KEY")

@pytest.fixture
def mock_env_no_access_key(monkeypatch):
    """ mock environment with no access key """
    monkeypatch.delenv("ACCESS_KEY", raising=False)
