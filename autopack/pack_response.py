from dataclasses import dataclass
from typing import Any

from dataclasses_json import dataclass_json


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
        return f"{self.author}_{self.repo}_{self.name}".replace("-", "_").replace(
            " ", "_"
        )

    def repo_url(self) -> str:
        return f"https://github.com/{self.author}/{self.repo}.git"
