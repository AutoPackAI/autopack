from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PackResponse:
    """Class to get just enough data to find the pack class"""

    package_path: str
    class_name: str
    repo_url: str
