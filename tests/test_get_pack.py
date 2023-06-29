from unittest.mock import Mock, call, patch

import pytest

from autopack.api import PackResponse
from autopack.errors import AutoPackNotFoundError, AutoPackNotInstalledError
from autopack.get_pack import (get_all_installed_packs, get_pack, try_get_pack,
                               try_get_packs)
from autopack.installation import install_pack
from tests.data.packs.noop import NoopPack


@pytest.fixture
def pack_response_valid():
    return PackResponse(
        pack_id="some_author/my_packs/NoopPack",
        author="some_author",
        repo="my_packs",
        module_path="noop",
        description="A pack for doing nothing",
        name="NoopPack",
        dependencies=["langchain", "requests"],
        source="git",
        run_args={
            "query": {
                "type": "string",
                "description": "What you want to do nothing about",
            }
        },
        init_args={
            "api_key": {"type": "string", "description": "The API key to nowhere"}
        },
    )


@pytest.fixture
def installed_valid_pack(mock_requests_get, pack_response_valid, mock_repo_url):
    # First install the pack
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = pack_response_valid.__dict__
    mock_requests_get.return_value = mock_response
    install_pack(pack_response_valid.pack_id)


@pytest.fixture
def pack_response_invalid_path(pack_response_valid):
    invalid_path_response = PackResponse(**pack_response_valid.__dict__)
    invalid_path_response.module_path = "some.bad.path"
    return invalid_path_response


@pytest.fixture
def pack_response_invalid_class(pack_response_valid):
    invalid_class_response = PackResponse(**pack_response_valid.__dict__)
    invalid_class_response.pack_id = "some/junk/pack"
    invalid_class_response.module_path = "tests.data.packs.invalid"
    invalid_class_response.name = "InvalidPack"
    return invalid_class_response


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_success(
    mock_get_pack_details, pack_response_valid, installed_valid_pack
):
    pack_id = pack_response_valid.pack_id
    mock_get_pack_details.return_value = pack_response_valid

    result = get_pack(pack_id)

    assert result.tool_class.__name__ == NoopPack.__name__
    assert result.pack_id == pack_response_valid.pack_id
    assert result.run_args == pack_response_valid.run_args
    assert result.init_args == pack_response_valid.init_args
    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_not_found(mock_get_pack_details):
    pack_id = "some_author/my_packs/NoopPack"
    mock_get_pack_details.return_value = None

    with pytest.raises(AutoPackNotFoundError):
        get_pack(pack_id)

    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_module_not_found(mock_get_pack_details, pack_response_invalid_path):
    pack_id = pack_response_invalid_path.pack_id
    mock_get_pack_details.return_value = pack_response_invalid_path

    with pytest.raises(AutoPackNotInstalledError):
        get_pack(pack_id)

    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_invalid_class(mock_get_pack_details, pack_response_invalid_class):
    pack_id = pack_response_invalid_class.pack_id
    mock_get_pack_details.return_value = pack_response_invalid_class

    with pytest.raises(AutoPackNotFoundError):
        get_pack(pack_id)

    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_try_get_pack_success(
    mock_get_pack_details, pack_response_valid, installed_valid_pack
):
    pack_id = pack_response_valid.pack_id
    mock_get_pack_details.return_value = pack_response_valid

    # TODO: Why does this work without it being installed lol
    result = try_get_pack(pack_id)

    assert result.tool_class.__name__ == NoopPack.__name__
    assert result.pack_id == pack_response_valid.pack_id
    assert result.run_args == pack_response_valid.run_args
    assert result.init_args == pack_response_valid.init_args
    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_try_get_pack_not_found(mock_get_pack_details):
    pack_id = "some_author/my_packs/NoopPack"
    mock_get_pack_details.return_value = None

    assert try_get_pack(pack_id) is None

    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_try_get_packs_success(
    mock_get_pack_details,
    pack_response_valid,
    pack_response_invalid_class,
    installed_valid_pack,
):
    mock_get_pack_details.side_effect = [
        pack_response_valid,
        pack_response_invalid_class,
    ]

    results = try_get_packs(
        [pack_response_valid.pack_id, "some/junk/pack"], quiet=False
    )

    assert len(results) == 1
    result = results[0]

    assert result.tool_class.__name__ == NoopPack.__name__
    assert result.pack_id == pack_response_valid.pack_id
    assert result.run_args == pack_response_valid.run_args
    assert result.init_args == pack_response_valid.init_args
    mock_get_pack_details.assert_has_calls(
        [
            call(pack_response_valid.pack_id, remote=False),
            call(pack_response_invalid_class.pack_id, remote=False),
        ]
    )


@patch("autopack.get_pack.get_pack_details")
def test_try_get_all_installed_packs(
    mock_get_pack_details, pack_response_valid, installed_valid_pack
):
    mock_get_pack_details.return_value = pack_response_valid

    results = get_all_installed_packs()

    assert len(results) == 1
    result = results[0]

    assert result.tool_class.__name__ == NoopPack.__name__
    assert result.pack_id == pack_response_valid.pack_id
    assert result.run_args == pack_response_valid.run_args
    assert result.init_args == pack_response_valid.init_args
    mock_get_pack_details.assert_called_with(pack_response_valid.pack_id, remote=False)
