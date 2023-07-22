import pytest

from tests.data.packs.noop import NoopPack
from tests.data.packs.summarization_pack import SummarizationPack


def test_sync_llm():
    def mock_llm(text_in: str):
        return text_in.upper()

    pack = SummarizationPack(llm=mock_llm)

    assert pack.run(text="some text") == "SUMMARIZE THE FOLLOWING TEXT:\nSOME TEXT"


@pytest.mark.asyncio
async def test_async_llm():
    async def mock_allm(text_in: str):
        return text_in.upper() + "!"

    pack = SummarizationPack(allm=mock_allm)

    assert await pack.arun(text="some text") == "SUMMARIZE THE FOLLOWING TEXT:\nSOME TEXT!"


def test_noop():
    assert NoopPack().run(query="some query") == "noop: some query"


@pytest.mark.asyncio
async def test_async_noop():
    assert await NoopPack().arun(query="some query") == "noop: some query"
