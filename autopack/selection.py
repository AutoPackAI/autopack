import json

from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage

from autopack.api import pack_search

TOOL_SELECTION_PROMPT = """
You are an autonomous AI Agent. I have a list of tools to choose from and a task I need you to accomplish. Recommend
tools that would be required for you to complete the task. Return only a comma-separated list of tool_ids and no
other content.

---- TASK ----
{user_input}
---- TOOLS ----
{tools_string}
"""


def select_packs(task_description: str, llm: BaseChatModel) -> list[str]:
    """Given a user input describing the task they wish to accomplish, return a list of Pack IDs that the given LLM
    thinks will be suitable for this task.

    This is good for a "pre-processing" step after receiving the task but before trying to solve it. This allows you
    to benefit from the wide tool selection while keeping your token usage low.

    You can then further filter, install the packs if desired, and then fetch them using get_pack().

    Args:
        task_description (str): A description of the task to be used when selecting tools
        llm (BaseChatModel): An LLM which will be used to evaluate the selection

    Returns:
        list[str]: A list of selected Pack IDs
    """

    packs = pack_search("")
    pack_summaries = []
    for pack in packs:
        pack_summaries.append(
            {
                "tool_id": pack.pack_id,
                "name": pack.name,
                "description": pack.description,
                "arguments": pack.run_args,
            }
        )

    tools_string = json.dumps(pack_summaries)
    prompt = TOOL_SELECTION_PROMPT.format(
        user_input=task_description, tools_string=tools_string
    )

    selected_packs = ask_llm(prompt, llm)

    return selected_packs


def ask_llm(prompt: str, llm: BaseChatModel) -> list[str]:
    """Encapsulate the OpenAI specific stuff to easier support other frameworks in the future"""
    message = HumanMessage(content=prompt)

    response = llm(messages=[message])

    return response.content.split(",")
