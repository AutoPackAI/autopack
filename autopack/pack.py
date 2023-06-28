from typing import Any, Type

from autopack.api import PackResponse


class Pack:
    """
    Class to describe the Pack that is returned from get_pack calls. Wraps the Tool and provides metadata about the
    pack.
    """

    def __init__(
        self,
        pack_id: str,
        author: str,
        repo: str,
        module_path: str,
        description: str,
        name: str,
        dependencies: list[str],
        source: str,
        args: dict[str, Any],
        init_args: dict[str, Any],
        tool: Type,
    ):
        self.pack_id = pack_id
        self.author = author
        self.repo = repo
        self.module_path = module_path
        self.description = description
        self.name = name
        self.dependencies = dependencies
        self.source = source
        self.args = args
        self.init_args = init_args
        self.tool = tool

    @classmethod
    def from_pack_data(cls, tool: Type, pack_data: PackResponse):
        return cls(
            pack_id=pack_data.pack_id,
            author=pack_data.author,
            repo=pack_data.repo,
            module_path=pack_data.module_path,
            description=pack_data.description,
            name=pack_data.name,
            dependencies=pack_data.dependencies,
            source=pack_data.source,
            args=pack_data.args,
            init_args=pack_data.init_args,
            tool=tool,
        )
