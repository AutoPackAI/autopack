from autopack.filesystem_emulation.file_manager import FileManager
from autopack.pack_config import PackConfig


class RAMFileManager(FileManager):
    """
    This class emulates a filesystem in RAM, storing files in a dictionary where keys are file paths and values are
    file content. Recommended for sandboxing or for testing.
    """

    def __init__(self, config: PackConfig = PackConfig.global_config()):
        super().__init__(config)
        self.files = {}

    def read_file(self, file_path: str) -> str:
        """Reads a file from the virtual file system in RAM.

        Args:
            file_path (str): The path to the file to be read.

        Returns:
            str: The content of the file. If the file does not exist, returns an error message.
        """
        if file_path in self.files:
            return self.files[file_path]
        else:
            return "Error: File not found"

    def write_file(self, file_path: str, content: str) -> str:
        """Writes to a file in the virtual file system in RAM.

        Args:
            file_path (str): The path to the file to be written to.
            content (str): The content to be written to the file.

        Returns:
            str: A success message indicating the file was written.
        """
        self.files[file_path] = content
        return f"Successfully wrote {len(content.encode('utf-8'))} bytes to {file_path}"

    async def awrite_file(self, file_path: str, content: str) -> str:
        return self.write_file(file_path, content)

    def delete_file(self, file_path: str) -> str:
        """Deletes a file from the virtual file system in RAM.

        Args:
            file_path (str): The path to the file to be deleted.

        Returns:
            str: A success message indicating the file was deleted. If the file does not exist, returns an error message.
        """
        if file_path in self.files:
            del self.files[file_path]
            return f"Successfully deleted file {file_path}."
        else:
            return f"Error: File not found '{file_path}'"

    def list_files(self, dir_path: str) -> str:
        """Lists all files in the specified directory in the virtual file system in RAM.

        Args:
            dir_path (str): The path to the directory to list files from.

        Returns:
            str: A list of all files in the directory. If the directory does not exist, returns an error message.
        """
        # For simplicity, let's assume that all keys in `self.files` are file paths, and to list files in a directory,
        # we just need to find all keys that start with `dir_path`.
        files_in_dir = [
            file_path
            for file_path in self.files.keys()
            if file_path.startswith(dir_path) and file_path not in self.IGNORE_FILES
        ]
        if files_in_dir:
            return "\n".join(files_in_dir)
        else:
            return f"Error: No such directory {dir_path}."
