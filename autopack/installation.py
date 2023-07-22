import importlib
import os
import shutil
import subprocess

from git import Repo

from autopack.api import PackResponse, get_pack_details
from autopack.errors import AutoPackError, AutoPackInstallationError
from autopack.get_pack import try_get_pack, get_pack
from autopack.pack import Pack
from autopack.utils import (
    find_or_create_autopack_dir,
    load_metadata_file,
    write_metadata_file,
    extract_unique_directory_name,
)


def is_dependency_installed(dependency: str) -> bool:
    try:
        importlib.import_module(dependency)
        return True
    except ImportError:
        return False


def install_dependency(dependency: str, quiet=True):
    try:
        subprocess.check_output(
            ["pip", "install", dependency],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        if not quiet:
            print(f"{dependency} has been successfully installed.")
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"Installation of {dependency} failed with the following error:")
            print(e.output)


def ask_to_install_dependencies(dependencies: list[str], force=False, quiet=True):
    for dependency in dependencies:
        if is_dependency_installed(dependency):
            continue

        if force:
            install_dependency(dependency)
        else:
            if not quiet:
                print(f"This pack requires the dependency {dependency} to be installed. Continue?")
            agree = input("[Yn]")
            if agree.lower() == "y" or agree == "":
                install_dependency(dependency, quiet=quiet)
            elif not quiet:
                print(f"Skipping install of {dependency}")


def install_from_git(pack_data: PackResponse, quiet=True) -> str:
    autopack_dir = find_or_create_autopack_dir()

    url = pack_data.repo_url
    pack_path = os.path.join(autopack_dir, *extract_unique_directory_name(pack_data.repo_url).split("/"))

    if os.path.exists(pack_path):
        if not quiet:
            print("Repo already exists, pulling updates")
        Repo(pack_path).remotes.origin.pull()
    else:
        if not quiet:
            print(f"Cloning repo into {pack_path}")
        Repo.clone_from(url, pack_path)

    return pack_path


def update_metadata_file(pack_id: str, pack_response: PackResponse):
    metadata = load_metadata_file()
    metadata[pack_id] = pack_response.__dict__

    write_metadata_file(metadata)


def install_pack(pack_id: str, force_dependencies=False, quiet=True) -> type[Pack]:
    if not quiet:
        print(f"Installing pack: {pack_id}")

    find_or_create_autopack_dir()

    pack = try_get_pack(pack_id)
    if pack:
        if not quiet:
            print(f"Pack {pack_id} already installed.")
        return pack

    try:
        pack_data = get_pack_details(pack_id, remote=True)

        if not pack_data:
            raise AutoPackInstallationError("Could not find pack details")
    except AutoPackError as e:
        # Maybe do something else
        raise AutoPackInstallationError(f"Could not install pack {e}")
    except BaseException as e:
        raise AutoPackInstallationError(f"Could not install pack {e}")

    try:
        git_dir = install_from_git(pack_data, quiet=quiet)

        update_metadata_file(pack_id, pack_data)
        pack = get_pack(pack_id)

        if pack:
            if pack.dependencies:
                ask_to_install_dependencies(pack.dependencies, force=force_dependencies, quiet=quiet)
            return pack
    except Exception as e:
        raise AutoPackInstallationError(f"Couldn't install pack due to error {e}")

    # Clean up bad repo directories to make sure there aren't bad packs in the .autopack dir
    if git_dir and os.path.isdir(git_dir):
        shutil.rmtree(git_dir)

    raise AutoPackInstallationError("Error: Installation completed but pack could still not be found.")
