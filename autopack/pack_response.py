from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PackResponse:
    """Class to store metadata about a (possibly uninstalled) pack"""

    pack_id: str
    package_path: str
    class_name: str
    repo_url: str
