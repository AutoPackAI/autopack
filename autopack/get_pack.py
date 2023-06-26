import importlib
import inspect
import os
import sys
from types import ModuleType
from typing import Type, Union

from autopack.api import PackResponse, get_pack_details
from autopack.errors import AutoPackError, AutoPackLoadError, AutoPackNotFoundError, AutoPackNotInstalledError


def try_get_pack(pack_id: str, quiet=False) -> Union[Type, None]:
    """
    Get a pack based on its ID, in `author/repo_name/pack_name` format. Same as `get_pack` but does not raise an
    Exception. If there is a problem finding or loading a pack it will return None.

    Args:
        pack_id (str): The ID of the pack to fetch.
        quiet (bool, Optional): If True, won't print any output

    Returns:
        BaseTool or None: The fetched pack as a LangChain BaseTool object, None if the pack could not be loaded
    """

    try:
        return get_pack(pack_id, quiet=quiet)
    except AutoPackError:
        return None


def get_pack(pack_id: str, quiet=False) -> Type:
    """
    Get a pack based on its ID, in `author/repo_name/pack_name` format.

    Args:
        pack_id (str): The ID of the pack to fetch.
        quiet (bool, Optional): If True, won't print any output

    Returns:
        BaseTool: The fetched pack as a LangChain BaseTool object

    Raises:
        AutoPackFetchError: If there was an error during the data fetch.
        AutoPackNotInstalledError: If the pack was found but not installed.
        AutoPackNotFoundError: If no pack matching that ID was found.
        AutoPackLoadError: If the pack was found but there was an error importing or finding the pack class.
    """
    pack_data = get_pack_details(pack_id)

    if not pack_data:
        raise AutoPackNotFoundError()

    return find_pack(pack_data, quiet=quiet)


def find_module(pack_data: PackResponse) -> ModuleType:
    module_path = pack_data.module_path

    # Just in case they already have it in their path for whatever reason
    try:
        return importlib.import_module(module_path)
    except:
        autopack_dir = find_or_create_autopack_dir()
        sys.path.insert(0, autopack_dir)

        try:
            return importlib.import_module(pack_data.pack_path() + "." + module_path)
        finally:
            sys.path.remove(autopack_dir)


def find_or_create_autopack_dir(depth=0) -> str:
    """Search in current and parent directories looking for .autopack"""
    autopack_dir = os.path.abspath(os.path.join(os.getcwd(), *[os.pardir] * depth, ".autopack"))

    if not os.path.exists(autopack_dir) or not os.path.isdir(autopack_dir):
        if depth > 3:
            raise ModuleNotFoundError(".autopack directory could not be found")
        return find_or_create_autopack_dir(depth=depth + 1)

    return autopack_dir


def find_pack(pack_data: PackResponse, quiet=False) -> Type:
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
                return obj

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

    base_class_names = [k.__name__ for k in klass.__bases__]
    roughly_adheres_to_interface = hasattr(klass, "run") or "BaseTool" in base_class_names
    if not roughly_adheres_to_interface:
        return False

    # Pack name is the class name
    if name == klass.__name__:
        return True

    # Pack class has a name class variable
    if hasattr(klass, "name"):
        if callable(klass.name):
            klass_name = klass.name()
        else:
            klass_name = klass.name
        return klass_name == name

    # Pack class has a __fields__ class variable (e.g. LangChain's BaseTool)
    if hasattr(klass, "__fields__"):
        name_field = klass.__fields__.get("name")
        return name_field and name_field.default == name

    return False
