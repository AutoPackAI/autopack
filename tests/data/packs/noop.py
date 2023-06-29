from langchain.tools import BaseTool


class NoopPack(BaseTool):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _run(self, query: str):
        return f"noop: {query}"

    async def _arun(self, *args, **kwargs):
        return self.run(*args, **kwargs)
