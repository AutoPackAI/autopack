from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

from tests.data.packs.noop import NoopPack


def test_init_langchain_tool():
    pack = NoopPack()
    tool = pack.init_langchain_tool()
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k-0613")

    agent = initialize_agent(
        [tool],
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    assert len(agent.tools) == 1
    assert agent.tools[0].name == "noop_pack"
