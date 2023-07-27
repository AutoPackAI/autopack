import os
from pathlib import Path

import aiofiles as aiofiles

from autopack.filesystem_emulation.file_manager import FileManager
from autopack.pack_config import PackConfig


class WorkspaceFileManager(FileManager):
    """
    This class provides file operations restricted to a workspace directory on the local file system.
    """

    def __init__(self, config: PackConfig = PackConfig.global_config()):
        super().__init__(config)
        self.workspace_dir = Path(config.workspace_path)

    def read_file(self, file_path: str) -> str:
        """Reads a file from the workspace directory on the local file system.

        Args:
            file_path (str): The path to the file to be read, relative to the workspace directory.

        Returns:
            str: The content of the file. If the file does not exist, returns an error message.
        """
        absolute_path = self.workspace_dir / file_path
        if absolute_path.exists():
            with open(absolute_path, "r") as file:
                return file.read()
        else:
            return "Error: File not found"

    def write_file(self, file_path: str, content: str) -> str:
        """Writes to a file in the workspace directory on the local file system.

        Args:
            file_path (str): The path to the file to be written to, relative to the workspace directory.
            content (str): The content to be written to the file.

        Returns:
            str: A success message indicating the file was written.
        """
        absolute_path = self.workspace_dir / file_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        with open(absolute_path, "w+") as file:
            file.write(content)

        return f"Successfully wrote {len(content.encode('utf-8'))} bytes to {file_path}"

    async def awrite_file(self, file_path: str, content: str) -> str:
        """Writes to a file in the workspace directory on the local file system.

        Args:
            file_path (str): The path to the file to be written to, relative to the workspace directory.
            content (str): The content to be written to the file.

        Returns:
            str: A success message indicating the file was written.
        """
        absolute_path = self.workspace_dir / file_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(absolute_path, "w+") as file:
            await file.write(content)

        return f"Successfully wrote {len(content.encode('utf-8'))} bytes to {file_path}"

    def delete_file(self, file_path: str) -> str:
        """Deletes a file from the workspace directory on the local file system.

        Args:
            file_path (str): The path to the file to be deleted, relative to the workspace directory.

        Returns:
            str: A success message indicating the file was deleted. If the file does not exist, returns an error message.
        """
        absolute_path = self.workspace_dir / file_path
        if absolute_path.exists():
            os.remove(absolute_path)
            return f"Successfully deleted file {file_path}."
        else:
            return f"Error: File not found '{file_path}'"

    def list_files(self, dir_path: str) -> str:
        """Lists all files in the specified directory in the workspace directory on the local file system.

        Args:
            dir_path (str): The path to the directory to list files from, relative to the workspace directory.

        Returns:
            str: A list of all files in the directory. If the directory does not exist, returns an error message.
        """
        absolute_dir_path = self.workspace_dir / dir_path
        if absolute_dir_path.exists() and absolute_dir_path.is_dir():
            files_in_dir = absolute_dir_path.glob("*")
            return "\n".join(str(file) for file in files_in_dir if file not in self.IGNORE_FILES)
        else:
            return f"Error: No such directory {dir_path}."
