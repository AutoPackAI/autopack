from unittest.mock import Mock

import pytest

from autopack.api import API_URL, get_pack_details
from autopack.errors import AutoPackFetchError
from autopack.installation import install_pack
from tests.data.packs.noop import NoopPack


@pytest.fixture
def valid_pack_data():
    return {
        "pack_id": "autopack/tests/noop",
        "repo_url": "git@github.com:AutoPackAI/autopack.git",
        "package_path": "tests.data.packs.noop",
        "class_name": "NoopPack",
        "name": NoopPack.name,
        "description": NoopPack.description,
        "categories": NoopPack.categories,
        "run_args": [{"name": "query", "type": "string"}],
        "dependencies": [],
    }


def test_fetch_remote_pack_data_success(mock_requests_get, valid_pack_data):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_pack_data
    mock_requests_get.return_value = mock_response

    response = get_pack_details("pack_id", remote=True)

    mock_requests_get.assert_called_once_with(f"{API_URL}api/details", params={"id": "pack_id"})

    assert response.repo_url == valid_pack_data["repo_url"]
    assert response.package_path == valid_pack_data["package_path"]
    assert response.class_name == valid_pack_data["class_name"]


def test_fetch_remote_pack_data_invalid_response(mock_requests_get, valid_pack_data):
    valid_pack_data.pop("repo_url")

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_pack_data
    mock_requests_get.return_value = mock_response

    with pytest.raises(AutoPackFetchError):
        get_pack_details("pack_id", remote=True)

    mock_requests_get.assert_called_once_with(f"{API_URL}api/details", params={"id": "pack_id"})


def test_fetch_remote_pack_data_error_response(mock_requests_get, valid_pack_data):
    mock_response = Mock()
    mock_response.status_code = 503
    mock_requests_get.return_value = mock_response

    with pytest.raises(AutoPackFetchError):
        get_pack_details("pack_id", remote=True)

    mock_requests_get.assert_called_once_with(f"{API_URL}api/details", params={"id": "pack_id"})


def test_fetch_remote_pack_data_not_found_response(mock_requests_get, valid_pack_data):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    with pytest.raises(AutoPackFetchError):
        get_pack_details("pack_id", remote=True)

    mock_requests_get.assert_called_once_with(f"{API_URL}api/details", params={"id": "pack_id"})


def test_fetch_local_not_found(valid_pack_data):
    with pytest.raises(AutoPackFetchError):
        get_pack_details("pack_id")


@pytest.mark.skip
def test_fetch_local_exists(mock_requests_get, valid_pack_data):
    pack_id = "I need to create a pack remotely and then use that"
    # First install the pack
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_pack_data
    mock_requests_get.return_value = mock_response

    install_pack(pack_id)

    mock_requests_get.assert_called_once_with(f"{API_URL}api/details", params={"id": pack_id})

    response = get_pack_details(pack_id)

    assert response.repo_url == valid_pack_data["repo_url"]
    assert response.package_path == valid_pack_data["package_path"]
    assert response.class_name == valid_pack_data["class_name"]
