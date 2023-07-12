from langchain.tools import BaseTool


class NoopPack(BaseTool):
    name: str = "noop_pack"

    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__()

    def _run(self, query: str):
        return f"noop: {query}"

    async def _arun(self, *args, **kwargs):
        return self.run(*args, **kwargs)
