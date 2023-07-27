from unittest.mock import Mock, call, patch

import pytest

from autopack.api import PackResponse
from autopack.errors import AutoPackLoadError, AutoPackNotFoundError
from autopack.get_pack import get_all_installed_packs, get_pack, try_get_pack, try_get_packs
from autopack.installation import install_pack
from tests.data.packs.noop import NoopPack


@pytest.fixture
def pack_response_valid():
    return PackResponse(
        pack_id="autopack/tests/noop",
        repo_url="git@github.com:AutoPackAI/autopack.git",
        package_path="tests.data.packs.noop",
        class_name="NoopPack",
        name=NoopPack.name,
        dependencies=[],
        description=NoopPack.description,
        categories=NoopPack.categories,
        run_args=[{"name": "query", "type": "string"}],
    )


@pytest.fixture
def installed_valid_pack(mock_requests_get, pack_response_valid):
    # First install the pack
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = pack_response_valid.__dict__
    mock_requests_get.return_value = mock_response
    install_pack("")


@pytest.fixture
def pack_response_invalid_path(pack_response_valid):
    invalid_path_response = PackResponse(**pack_response_valid.__dict__)
    invalid_path_response.package_path = "some.bad.path"
    return invalid_path_response


@pytest.fixture
def pack_response_invalid_class(pack_response_valid):
    invalid_class_response = PackResponse(**pack_response_valid.__dict__)
    invalid_class_response.class_name = "InvalidClass"
    return invalid_class_response


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_success(mock_get_pack_details, pack_response_valid, installed_valid_pack):
    pack_id = "noop_pack"
    mock_get_pack_details.return_value = pack_response_valid

    result = get_pack(pack_id)

    assert result == NoopPack
    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_not_found(mock_get_pack_details):
    pack_id = "asdf"
    mock_get_pack_details.return_value = None

    with pytest.raises(AutoPackNotFoundError):
        get_pack(pack_id)

    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_module_not_found(mock_get_pack_details, pack_response_invalid_path):
    pack_id = "invalidmodule"
    mock_get_pack_details.return_value = pack_response_invalid_path

    with pytest.raises(AutoPackLoadError):
        get_pack(pack_id)

    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_get_pack_invalid_class(mock_get_pack_details, pack_response_invalid_class):
    pack_id = "invalidclass"
    mock_get_pack_details.return_value = pack_response_invalid_class

    with pytest.raises(AutoPackLoadError):
        get_pack(pack_id)

    mock_get_pack_details.assert_called_once_with(pack_id, remote=False)


@patch("autopack.get_pack.get_pack_details")
def test_try_get_pack_success(mock_get_pack_details, pack_response_valid, installed_valid_pack):
    pack_id = "noop_pack"
    mock_get_pack_details.return_value = pack_response_valid

    # TODO: Why does this work without it being installed lol
    result = try_get_pack(pack_id)

    assert result == NoopPack
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

    valid_pack_id = "valid pack id"
    invalid_pack_id = "bogus pack id"
    results = try_get_packs([valid_pack_id, invalid_pack_id])

    assert len(results) == 1
    result = results[0]

    assert result == NoopPack
    mock_get_pack_details.assert_has_calls(
        [
            call(valid_pack_id, remote=False),
            call(invalid_pack_id, remote=False),
        ]
    )


@patch("autopack.get_pack.get_pack_details")
def test_try_get_all_installed_packs(mock_get_pack_details, pack_response_valid, installed_valid_pack):
    mock_get_pack_details.return_value = pack_response_valid

    results = get_all_installed_packs()

    assert len(results) == 1
    result = results[0]

    assert result == NoopPack
    mock_get_pack_details.assert_called_with("", remote=False)
