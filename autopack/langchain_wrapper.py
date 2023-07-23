from langchain.tools import BaseTool
from pydantic import Field

from autopack import Pack


class LangchainWrapper(BaseTool):
    """Thin wrapper around a Pack to allow it to be a LangChain-compatible Tool"""

    pack: Pack = Field(..., description="The AutoPack Pack")

    def __init__(self, **kwargs):
        pack = kwargs.get("pack")
        kwargs["name"] = pack.name
        kwargs["description"] = pack.description
        kwargs["args_schema"] = pack.args_schema
        super().__init__(**kwargs)

    def _run(self, *args, **kwargs):
        return self.pack.run(*args, **kwargs)

    async def _arun(self, *args, **kwargs):
        return self.pack.arun(*args, **kwargs)

    def is_single_input(self) -> bool:
        return False
