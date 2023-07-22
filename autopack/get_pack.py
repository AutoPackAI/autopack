from typing import Union

from autopack.api import get_pack_details
from autopack.errors import AutoPackError, AutoPackNotFoundError
from autopack.pack import Pack
from autopack.utils import fetch_pack_object, load_metadata_file


def try_get_pack(pack_id: str, remote=False) -> Union[type[Pack], None]:
    """
    Get a pack based on its ID. Same as `get_pack` but does not raise an Exception. If there is a problem finding or
    loading a pack it will return None.

    Args:
        pack_id (str): The ID of the pack to fetch.
        quiet (bool, Optional): If True, won't print any output
        remote (bool, Optional): If True, will make network requests to fetch pack metadata

    Returns:
        Pack or None: The fetched pack, None if the pack could not be loaded
    """

    try:
        return get_pack(pack_id, remote=remote)
    except AutoPackError:
        return None


def get_all_installed_packs():
    """Returns all of the"""
    metadata = load_metadata_file()
    pack_ids = list(metadata.keys())
    return try_get_packs(pack_ids, remote=False)


def try_get_packs(pack_ids: list[str], remote=False) -> list[type[Pack]]:
    """
    Get a list of packs based on their IDs

    Args:
        pack_ids (list[str]): The IDs of the packs to fetch.
        quiet (bool, Optional): If True, won't print any output
        remote (bool, Optional): If True, will make network requests to fetch pack metadata

    Returns:
        list[Pack]: The successfully fetched packs
    """
    packs = []
    for pack_id in pack_ids:
        pack = try_get_pack(pack_id, remote)
        if pack:
            packs.append(pack)

    return packs


def get_pack(pack_id: str, remote=False) -> type[Pack]:
    """
    Get a pack based on its ID, in `author/repo_name/pack_name` format.

    Args:
        pack_id (str): The ID of the pack to fetch.
        quiet (bool, Optional): If True, won't print any output
        remote (bool, Optional): If True, will make network requests to fetch pack metadata

    Returns:
        Pack: The fetched pack

    Raises:
        AutoPackFetchError: If there was an error during the data fetch.
        AutoPackNotInstalledError: If the pack was found but not installed.
        AutoPackNotFoundError: If no pack matching that ID was found.
        AutoPackLoadError: If the pack was found but there was an error importing or finding the pack class.
    """
    pack_data = get_pack_details(pack_id, remote=remote)

    if not pack_data:
        raise AutoPackNotFoundError()

    return fetch_pack_object(pack_data)
