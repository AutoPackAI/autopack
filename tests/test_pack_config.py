from autopack.filesystem_emulation.ram_file_manager import RAMFileManager
from autopack.filesystem_emulation.workspace_file_manager import WorkspaceFileManager
from autopack.pack_config import PackConfig


def test_create():
    config = PackConfig.create()
    assert isinstance(config, PackConfig)
    assert isinstance(config.filesystem_manager, WorkspaceFileManager)


def test_global_config():
    config = PackConfig.create(workspace_path="asdf")
    PackConfig.set_global_config(config)
    assert PackConfig.global_config().workspace_path == config.workspace_path


def test_override_filesystem_manager():
    config = PackConfig.create()
    config.init_filesystem_manager(RAMFileManager)
    assert isinstance(config.filesystem_manager, RAMFileManager)
