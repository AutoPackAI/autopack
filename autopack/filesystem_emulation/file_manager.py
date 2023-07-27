from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from autopack.pack_config import PackConfig


class FileManager(ABC):
    # A few Packs will use poetry inside of the workspace, and the AI gets hella confused when these files are present.
    IGNORE_FILES = ["pyproject.toml", "poetry.lock"]

    def __init__(self, config: "PackConfig" = None):
        from autopack.pack_config import PackConfig

        self.config = config or PackConfig.global_config()

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        pass

    @abstractmethod
    def write_file(self, file_path: str, content: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> str:
        pass

    @abstractmethod
    def list_files(self, dir_path: str) -> str:
        pass
