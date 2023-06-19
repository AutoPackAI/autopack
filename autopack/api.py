import os
from dataclasses import dataclass
from typing import Any, Union
from urllib.parse import urljoin

import requests
from dataclasses_json import dataclass_json
from marshmallow import ValidationError

from autopack.errors import AutoPackFetchError

API_URL = os.environ.get("API_URL", "https://autopack.ai")


@dataclass_json
@dataclass
class PackResponse:
    pack_id: str
    author: str
    repository: str
    module_path: str
    description: str
    name: str
    dependencies: list[str]
    source: str
    arguments: dict[str, Any]

    def pack_path(self) -> str:
        return f"{self.author}-{self.repository}-{self.name}"


def get_pack_data(pack_id: str) -> Union[PackResponse, None]:
    endpoint = "/packs/get"
    url = urljoin(API_URL, endpoint)
    params = {"id": pack_id}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        try:
            return PackResponse(**data)
        except (ValidationError, TypeError) as e:
            message = f"Pack fetch received invalid data: {e}"
            print(message)
            raise AutoPackFetchError(message)

    elif response.status_code <= 500:
        print(f"Error: {response.status_code}")
        return None
    else:
        print(f"Error: {response.status_code}")
        error_message = f"Error: {response.status_code}"
        raise AutoPackFetchError(error_message)
