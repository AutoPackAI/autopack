from dataclasses import dataclass
from typing import Any

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PackSearchResponse:
    """Class for display of search results"""

    pack_id: str
    package_path: str
    class_name: str
    repo_url: str
    name: str
    description: str
    dependencies: str
    run_args: dict[str, Any]
    categories: list[str]
