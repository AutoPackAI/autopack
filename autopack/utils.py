import importlib
import inspect
import json
import os
import sys
from json import JSONDecodeError
from types import ModuleType
from typing import Any, Type

from autopack.errors import AutoPackLoadError, AutoPackNotFoundError, AutoPackNotInstalledError
from autopack.pack import Pack
from autopack.pack_response import PackResponse


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

    autopack_dir = os.path.abspath(os.path.join(os.getcwd(), *[os.pardir] * depth, ".autopack"))

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


def find_module(pack_data: PackResponse) -> ModuleType:
    autopack_dir = find_or_create_autopack_dir()
    module_path = pack_data.module_path
    pack_module_path = os.path.join(autopack_dir, pack_data.pack_path())

    sys.path.insert(0, autopack_dir)
    sys.path.insert(0, pack_module_path)

    try:
        return importlib.import_module(module_path)
    finally:
        sys.path.remove(autopack_dir)
        sys.path.remove(pack_module_path)


def fetch_pack_object(pack_data: PackResponse, quiet=False) -> Pack:
    try:
        module = find_module(pack_data)
        if not module:
            message = (
                f"Pack {pack_data.pack_id} could not be found. Either it is misconfigured or .autopack directory not "
                f"found"
            )
            raise AutoPackNotFoundError(message)

        for _, obj in inspect.getmembers(module):
            if is_valid_pack(obj, pack_data.name):
                return Pack(**{"tool_class": obj, **pack_data.__dict__})

        message = f"Pack {pack_data.pack_id} found, but {pack_data.name} is not found in its module"
        raise AutoPackNotFoundError(message)
    except ModuleNotFoundError:
        message = (
            f"Pack {pack_data.pack_id} is available but not installed. To install: autopack install {pack_data.pack_id}"
        )
        if not quiet:
            print(message)
        raise AutoPackNotInstalledError(message)
    except (ImportError, AttributeError) as e:
        message = f"Error loading {pack_data.pack_id}: {e}"
        if not quiet:
            print(message)
        raise AutoPackLoadError(message)


def is_valid_pack(klass: Type, name: str):
    if not inspect.isclass(klass):
        return False

    if hasattr(klass, "__fields__"):
        name_field = klass.__fields__.get("name")
        if name_field and name_field.default:
            snaked_name = name_field.default.lower().replace(" ", "_")
            return name_field and snaked_name == name

    return False
