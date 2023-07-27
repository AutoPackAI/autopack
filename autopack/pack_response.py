from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PackResponse:
    """Class to store metadata about a (possibly uninstalled) pack"""

    pack_id: str
    package_path: str
    class_name: str
    repo_url: str
    name: str
    description: str
    dependencies: list[str] = field(default_factory=list)
    run_args: dict[str, dict[str, str]] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
