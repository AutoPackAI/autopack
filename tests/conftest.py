import os
import shutil
import sys
from unittest.mock import patch

import pytest

from autopack.api import PackResponse


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


@pytest.fixture(autouse=True)
def setup_autopack_dir(go_to_tmpdir):
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dot_autopack")
    destination_dir = ".autopack"

    if os.path.isdir(destination_dir):
        shutil.rmtree(destination_dir)
    shutil.copytree(source_dir, destination_dir)


@pytest.fixture
def mock_repo_url():
    with patch.object(PackResponse, "repo_url") as mock:
        source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "packs")
        mock.return_value = source_dir
        yield mock


@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch("requests.get")
