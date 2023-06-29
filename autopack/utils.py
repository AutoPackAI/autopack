import json
import os
from json import JSONDecodeError
from typing import Any


def find_or_create_autopack_dir(depth=0) -> str:
    """Try to find a suitable .autopack directory. Tries in this order:
    1. Directory specified in environment variable AUTOPACK_DIR
    2. Existing .autopack directory in current directory
    3. Existing .autopack directory up to 3 directories up
    4. Creates an .autopack directory in current directory
    """
    env_dir = os.environ.get("AUTOPACK_DIR")
    if env_dir:
        return env_dir

    autopack_dir = os.path.abspath(
        os.path.join(os.getcwd(), *[os.pardir] * depth, ".autopack")
    )

    if not os.path.exists(autopack_dir) or not os.path.isdir(autopack_dir):
        if depth > 3:
            os.makedirs(".autopack", exist_ok=True)
            return ".autopack"
        return find_or_create_autopack_dir(depth=depth + 1)

    return autopack_dir


def load_metadata_file() -> dict[str, Any]:
    """Return the parsed contents of the metadata file, returning an empty dict if not found or otherwise failed"""
    metadata_dir = find_or_create_autopack_dir()
    metadata_file = os.path.join(metadata_dir, "pack_metadata.json")

    if not os.path.exists(metadata_file):
        return {}

    with open(metadata_file, "r") as f:
        try:
            return json.load(f)
        except JSONDecodeError:
            return {}


def write_metadata_file(data: dict[str, Any]):
    metadata_dir = find_or_create_autopack_dir()
    metadata_file = os.path.join(metadata_dir, "pack_metadata.json")

    with open(metadata_file, "w+") as f:
        json.dump(data, f)
