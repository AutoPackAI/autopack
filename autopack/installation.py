import importlib
import os
import subprocess

from git import Repo

from autopack.api import PackResponse, get_pack_details
from autopack.errors import AutoPackError
from autopack.get_pack import try_get_pack


def is_dependency_installed(dependency: str) -> bool:
    try:
        importlib.import_module(dependency)
        return True
    except ImportError:
        return False


def install_dependency(dependency: str):
    try:
        subprocess.check_output(
            ["pip", "install", dependency],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        print(f"{dependency} has been successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Installation of {dependency} failed with the following error:")
        print(e.output)


def ask_to_install_dependencies(dependencies: list[str], force=False):
    for dependency in dependencies:
        if is_dependency_installed(dependency):
            continue

        if force:
            install_dependency(dependency)
        else:
            print(f"This pack requires the dependency {dependency} to be installed. Continue?")
            agree = input("[Yn]")
            if agree.lower() == "y" or agree == "":
                install_dependency(dependency)
            else:
                print(f"Skipping install of {dependency}")


def install_from_git(pack_data: PackResponse):
    os.makedirs(".autopack", exist_ok=True)

    url = f"https://github.com/{pack_data.author}/{pack_data.repository}.git"
    pack_path = os.path.join(".autopack", pack_data.pack_path())

    if os.path.exists(pack_path):
        print("Repo already exists, pulling updates")
        Repo(pack_path).remotes.origin.pull()
    else:
        print(f"Cloning repo into {pack_path}")
        Repo.clone_from(url, pack_path)


def install_pack(pack_id: str, force_dependencies=False):
    print(f"Installing pack: {pack_id}")
    os.makedirs(".autopack", exist_ok=True)

    pack = try_get_pack(pack_id, quiet=True)
    if pack:
        print(f"Pack {pack_id} already installed.")
        return True

    try:
        pack_data = get_pack_details(pack_id)

        if not pack_data:
            return False
        ask_to_install_dependencies(pack_data.dependencies, force_dependencies)
    except AutoPackError as e:
        # Maybe do something else
        print(f"Could not install pack {e}")
        return False
    except BaseException as e:
        print(f"Could not install pack {e}")
        return False

    if pack_data.source == "git":
        install_from_git(pack_data)

    pack = try_get_pack(pack_id, quiet=True)
    if pack:
        return True

    print("Error: Installation completed but pack could still not be found.")
    return False
