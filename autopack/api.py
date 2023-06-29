import json
import os
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any
from urllib.parse import urljoin

import requests
from dataclasses_json import dataclass_json
from marshmallow import ValidationError

from autopack.errors import AutoPackFetchError
from autopack.utils import find_or_create_autopack_dir

API_URL = os.environ.get("AUTOPACK_API_URL", "https://autopack.ai/")


@dataclass_json
@dataclass
class PackResponse:
    """Class to map Pack properties from the API. Internal use only."""

    pack_id: str
    author: str
    repo: str
    module_path: str
    description: str
    name: str
    dependencies: list[str]
    source: str
    run_args: dict[str, Any]
    init_args: dict[str, Any]

    def pack_path(self) -> str:
        return f"{self.author}_{self.repo}_{self.name}".replace("-", "_")

    def repo_url(self) -> str:
        return f"https://github.com/{self.author}/{self.repo}.git"


def get_pack_details(pack_id: str, remote=False) -> PackResponse:
    if remote:
        return get_pack_details_remotely(pack_id)

    return get_pack_details_locally(pack_id)


def get_pack_details_locally(pack_id: str) -> PackResponse:
    metadata_dir = find_or_create_autopack_dir()

    metadata_file = os.path.join(metadata_dir, "pack_metadata.json")

    if not os.path.exists(metadata_file):
        raise AutoPackFetchError(
            f"Metadata file does not exist, please install or re-install {pack_id}."
        )

    with open(metadata_file, "r") as f:
        try:
            metadata = json.load(f)
        except JSONDecodeError as e:
            raise AutoPackFetchError(
                f"Could  can't fetch locally. Please install or re-install {pack_id}. {e}"
            )

    pack_metadata = metadata.get(pack_id)
    if not pack_metadata:
        raise AutoPackFetchError(
            f"Could  can't find pack locally. Please install {pack_id}"
        )

    return PackResponse(**pack_metadata)


def get_pack_details_remotely(pack_id: str) -> PackResponse:
    endpoint = "/api/details"

    url = urljoin(API_URL, endpoint)
    params = {"id": pack_id}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        try:
            return PackResponse(**data)
        except (ValidationError, TypeError) as e:
            message = f"Pack fetch received invalid data: {e}"
            raise AutoPackFetchError(message)

    elif response.status_code <= 500:
        raise AutoPackFetchError(f"Error: {response.status_code}")
    else:
        raise AutoPackFetchError(f"Error: {response.status_code}")


def pack_search(query: str) -> list[PackResponse]:
    endpoint = "/api/search"
    url = urljoin(API_URL, endpoint)
    params = {"query": query}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        try:
            return [PackResponse(**datum) for datum in data["packs"]]
        except (ValidationError, TypeError) as e:
            message = f"Pack fetch received invalid data: {e}"
            print(message)
            raise AutoPackFetchError(message)

    elif response.status_code <= 500:
        print(f"Error: {response.status_code}")
        return []
    else:
        print(f"Error: {response.status_code}")
        error_message = f"Error: {response.status_code}"
        raise AutoPackFetchError(error_message)
