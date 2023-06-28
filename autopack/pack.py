from typing import Any, Type

from langchain.tools import BaseTool

from autopack.api import PackResponse


class Pack(BaseTool):
    """
    Class to describe the Pack that is returned from get_pack calls. Wraps the Tool and provides metadata about the
    pack.
    """

    pack_id: str
    author: str
    repo: str
    module_path: str
    description: str
    name: str
    dependencies: list[str]
    source: str
    run_args: dict[str, Any]
    init_args: dict[str, Any]
    # TODO/FIXME: This isn't guaranteed to be an actual BaseTool, by design, but typechecking complains otherwise
    tool: Type[BaseTool]

    def init_tool(self, init_args: dict[str, Any] = None):
        init_args = init_args or {}
        is_valid = validate_tool_args(self.init_args, init_args)
        # TODO: Error handling on invalid args
        if is_valid:
            self.tool(**init_args)

    def _run(self, *args, **kwargs):
        is_valid = validate_tool_args(self.run_args, kwargs)
        # TODO: Error handling on invalid args
        if is_valid:
            if hasattr(self.tool, "_run"):
                return self.tool._run(self, *args, **kwargs)
            else:
                return self.run(*args, **kwargs)

    async def _arun(self, *args, **kwargs):
        if hasattr(self.tool, "_run"):
            return await self.tool._arun(*args, **kwargs)
        else:
            return await self.arun(*args, **kwargs)

    @property
    def args(self) -> dict:
        return self.run_args

    @property
    def is_single_input(self) -> bool:
        """Hack on top of BaseTool to allow 0-arg tools"""
        keys = {k for k in self.args if k != "kwargs"}
        return len(keys) <= 1

    @classmethod
    def from_pack_data(cls, tool: BaseTool, pack_data: PackResponse):
        return cls(
            pack_id=pack_data.pack_id,
            author=pack_data.author,
            repo=pack_data.repo,
            module_path=pack_data.module_path,
            description=pack_data.description,
            name=pack_data.name,
            dependencies=pack_data.dependencies,
            source=pack_data.source,
            run_args=pack_data.run_args,
            init_args=pack_data.init_args,
            tool=tool,
        )


def validate_tool_args(spec: dict[str, Any], actual: dict[str, Any]):
    # TODO: This. Plus maybe some helpful errors?
    return True
