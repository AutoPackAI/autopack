from unittest.mock import patch

import pytest

from autopack.api import PackResponse
from autopack.errors import AutoPackNotFoundError, AutoPackNotInstalledError
from autopack.get_pack import get_pack, try_get_pack
from tests.data.packs.noop import NoopPack


@pytest.fixture
def pack_response_valid():
    return PackResponse(
        pack_id="some_author/my_packs/NoopPack",
        author="some_author",
        repository="my_packs",
        module_path="tests.data.packs.noop",
        description="A pack for doing nothing",
        name="NoopPack",
        dependencies=["langchain", "requests"],
        source="pypi",
        arguments={
            "query": {
                "type": "string",
                "description": "What you want to do nothing about",
            }
        },
    )


@pytest.fixture
def pack_response_invalid_path(pack_response_valid):
    pack_response_valid.module_path = "some.bad.path"
    return pack_response_valid


@pytest.fixture
def pack_response_invalid_class(pack_response_valid):
    pack_response_valid.module_path = "tests.data.packs.invalid"
    pack_response_valid.name = "InvalidPack"
    return pack_response_valid


@patch("autopack.get_pack.get_pack_data")
def test_get_pack_success(mock_get_pack_data, pack_response_valid):
    pack_id = pack_response_valid.pack_id
    mock_get_pack_data.return_value = pack_response_valid

    result = get_pack(pack_id)

    assert result == NoopPack
    mock_get_pack_data.assert_called_once_with(pack_id)


@patch("autopack.get_pack.get_pack_data")
def test_get_pack_not_found(mock_get_pack_data):
    pack_id = "some_author/my_packs/NoopPack"
    mock_get_pack_data.return_value = None

    with pytest.raises(AutoPackNotFoundError):
        get_pack(pack_id)

    mock_get_pack_data.assert_called_once_with(pack_id)


@patch("autopack.get_pack.get_pack_data")
def test_get_pack_module_not_found(mock_get_pack_data, pack_response_invalid_path):
    pack_id = pack_response_invalid_path.pack_id
    mock_get_pack_data.return_value = pack_response_invalid_path

    with pytest.raises(AutoPackNotInstalledError):
        get_pack(pack_id)

    mock_get_pack_data.assert_called_once_with(pack_id)


@patch("autopack.get_pack.get_pack_data")
def test_get_pack_invalid_class(mock_get_pack_data, pack_response_invalid_class):
    pack_id = pack_response_invalid_class.pack_id
    mock_get_pack_data.return_value = pack_response_invalid_class

    with pytest.raises(AutoPackNotFoundError):
        get_pack(pack_id)

    mock_get_pack_data.assert_called_once_with(pack_id)


@patch("autopack.get_pack.get_pack_data")
def test_try_get_pack_success(mock_get_pack_data, pack_response_valid):
    pack_id = pack_response_valid.pack_id
    mock_get_pack_data.return_value = pack_response_valid

    result = try_get_pack(pack_id)

    assert result == NoopPack
    mock_get_pack_data.assert_called_once_with(pack_id)


@patch("autopack.get_pack.get_pack_data")
def test_try_get_pack_not_found(mock_get_pack_data):
    pack_id = "some_author/my_packs/NoopPack"
    mock_get_pack_data.return_value = None

    assert try_get_pack(pack_id) is None

    mock_get_pack_data.assert_called_once_with(pack_id)