from unittest.mock import Mock

import pytest

from autopack.api import API_URL, get_pack_details
from autopack.errors import AutoPackFetchError


@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch("requests.get")


@pytest.fixture
def valid_pack_data():
    return {
        "pack_id": "some_author/my_packs/WebSearch",
        "author": "some_author",
        "repo": "my_packs",
        "module_path": "my_packs.web_search",
        "description": "A pack for web searching",
        "name": "WebSearch",
        "dependencies": ["langchain", "requests"],
        "source": "git",
        "args": {"query": "python", "limit": 10},
        "init_args": {
            "api_key": {"type": "string", "description": "The API key to nowhere"}
        },
    }


def test_fetch_pack_data_success(mock_requests_get, valid_pack_data):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_pack_data
    mock_requests_get.return_value = mock_response

    response = get_pack_details("pack_id")

    mock_requests_get.assert_called_once_with(
        f"{API_URL}api/details", params={"id": "pack_id"}
    )

    assert response.pack_id == valid_pack_data["pack_id"]
    assert response.author == valid_pack_data["author"]
    assert response.repo == valid_pack_data["repo"]
    assert response.module_path == valid_pack_data["module_path"]
    assert response.description == valid_pack_data["description"]
    assert response.dependencies == valid_pack_data["dependencies"]
    assert response.args == valid_pack_data["args"]


def test_fetch_pack_data_invalid_response(mock_requests_get, valid_pack_data):
    valid_pack_data.pop("name")

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_pack_data
    mock_requests_get.return_value = mock_response

    with pytest.raises(AutoPackFetchError):
        get_pack_details("pack_id")

    mock_requests_get.assert_called_once_with(
        f"{API_URL}api/details", params={"id": "pack_id"}
    )


def test_fetch_pack_data_error_response(mock_requests_get, valid_pack_data):
    mock_response = Mock()
    mock_response.status_code = 503
    mock_requests_get.return_value = mock_response

    with pytest.raises(AutoPackFetchError):
        get_pack_details("pack_id")

    mock_requests_get.assert_called_once_with(
        f"{API_URL}api/details", params={"id": "pack_id"}
    )


def test_fetch_pack_data_not_found_response(mock_requests_get, valid_pack_data):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    assert get_pack_details("pack_id") is None

    mock_requests_get.assert_called_once_with(
        f"{API_URL}api/details", params={"id": "pack_id"}
    )
