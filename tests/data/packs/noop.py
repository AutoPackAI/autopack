from pydantic import BaseModel, Field

from autopack import Pack


class NoopArgs(BaseModel):
    query: str = Field(..., description="The thing to do nothing about")


class NoopPack(Pack):
    name = "noop_pack"
    description = "Does nothing"
    categories = ["Nothingness"]
    args_schema = NoopArgs

    def _run(self, query: str):
        return f"noop: {query}"

    async def _arun(self, query: str):
        return self.run(query=query)
