from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional

from pydantic import Field, BaseSettings

from autopack.filesystem_emulation.file_manager import FileManager

if TYPE_CHECKING:
    from autopack import Pack


class InstallerStyle(str, Enum):
    # Packs and dependencies are automatically installed on use
    automatic = "automatic"
    # Packs, but not dependencies, are installed automatically on use
    semiautomatic = "semiautomatic"
    # Packs installed either through CLI or through your own code calling `install_pack`
    manual = "manual"


class PackConfig(BaseSettings):
    """
    Class for defining the configuration of AutoPack. This will either be set by:
    - A custom instantiated class or subclass, and then passed to the various autopack functions
    - A custom instantiated class or subclass, and then set as the global config
    - An automatically-configured global config based on environment variables and hard-coded defaults

    For each of these configuration settings there is a corresponding environment variable prefixed with `AUTOPACK_`,
    e.g.: AUTOPACK_FILESYSTEM_TYPE, AUTPACK_WORKSPACE_PATH
    """

    _global_config: ClassVar["PackConfig"] = None
    filesystem_manager: Optional[FileManager] = None

    class Config:
        env_prefix = "AUTOPACK_"

    workspace_path: str = Field(
        description="The directory for artifact storage and storage of working files.", default="workspace"
    )
    installer_style: InstallerStyle = Field(
        description="Style and permissiveness of Pack installation", default=InstallerStyle.automatic
    )
    restrict_code_execution: bool = Field(
        description="If True will signal to Packs that they should not execute code", default=False
    )
    # Not implemented yet
    local_packs: list[type["Pack"]] = Field(
        description="A list of local Pack classes that you wish to be included in the selection process",
        default_factory=list,
    )

    @classmethod
    def set_global_config(cls, config_obj: "PackConfig" = None) -> "PackConfig":
        """
        Set the default global config to either a PackConfig object of your choice, or `None` to use the default.
        """
        cls._global_config = config_obj or cls()
        return cls._global_config

    @classmethod
    def global_config(cls) -> "PackConfig":
        return cls._global_config or cls.set_global_config()

    def init_filesystem_manager(self, file_manager: type["FileManager"] = None):
        if file_manager:
            # Override previous / set new manager
            self.filesystem_manager = file_manager(self)
        elif not self.filesystem_manager:
            # Default
            from autopack.filesystem_emulation.workspace_file_manager import WorkspaceFileManager

            self.filesystem_manager = WorkspaceFileManager(self)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.init_filesystem_manager()
        return instance

    @property
    def automatically_install_dependencies(self) -> bool:
        return self.installer_style == InstallerStyle.automatic
