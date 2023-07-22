from pydantic import BaseModel, Field

from autopack import Pack


class SummarizationArgs(BaseModel):
    text: str = Field(..., description="The text to summarize")


class SummarizationPack(Pack):
    name = "text_summarization"
    description = "Summarizes the given text"
    categories = ["Text"]
    args_schema = SummarizationArgs

    def _run(self, text: str) -> str:
        return self.call_llm(f"Summarize the following text:\n{text}")

    async def _arun(self, text: str) -> str:
        return await self.acall_llm(f"Summarize the following text:\n{text}")
