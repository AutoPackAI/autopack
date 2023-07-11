import importlib
import os
import shutil
import subprocess

from git import Repo

from autopack.api import PackResponse, get_pack_details
from autopack.errors import AutoPackError, AutoPackInstallationError
from autopack.get_pack import try_get_pack
from autopack.pack import Pack
from autopack.utils import find_or_create_autopack_dir, load_metadata_file, write_metadata_file


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


def install_from_git(pack_data: PackResponse) -> str:
    autopack_dir = find_or_create_autopack_dir()

    url = pack_data.repo_url()
    pack_path = os.path.join(autopack_dir, pack_data.pack_path())

    if os.path.exists(pack_path):
        print("Repo already exists, pulling updates")
        Repo(pack_path).remotes.origin.pull()
    else:
        print(f"Cloning repo into {pack_path}")
        Repo.clone_from(url, pack_path)

    return pack_path


def update_metadata_file(pack: PackResponse):
    metadata = load_metadata_file()
    metadata[pack.pack_id] = {
        "pack_id": pack.pack_id,
        "author": pack.author,
        "repo": pack.repo,
        "module_path": pack.module_path,
        "description": pack.description,
        "name": pack.name,
        "dependencies": pack.dependencies,
        "source": pack.source,
        "run_args": pack.run_args,
        "init_args": pack.init_args,
    }

    write_metadata_file(metadata)


def install_pack(pack_id: str, force_dependencies=False) -> Pack:
    print(f"Installing pack: {pack_id}")
    find_or_create_autopack_dir()

    pack = try_get_pack(pack_id, quiet=False)
    if pack:
        print(f"Pack {pack_id} already installed.")
        return pack

    try:
        pack_data = get_pack_details(pack_id, remote=True)

        if not pack_data:
            raise AutoPackInstallationError("Could not find pack details")

        ask_to_install_dependencies(pack_data.dependencies, force_dependencies)
    except AutoPackError as e:
        # Maybe do something else
        raise AutoPackInstallationError(f"Could not install pack {e}")
    except BaseException as e:
        raise AutoPackInstallationError(f"Could not install pack {e}")

    git_dir = ""
    try:
        if pack_data.source == "git":
            git_dir = install_from_git(pack_data)

        update_metadata_file(pack_data)
        pack = try_get_pack(pack_id, quiet=False)

        if pack:
            return pack

    except Exception as e:
        raise AutoPackInstallationError(f"Couldn't install pack due to error {e}")

    if git_dir and os.path.isdir(git_dir):
        shutil.rmtree(git_dir)

    raise AutoPackInstallationError("Error: Installation completed but pack could still not be found.")
