import json
from json import JSONDecodeError

from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage

from autopack.api import pack_search

TOOL_SELECTION_PROMPT = """
I have a list of tools to choose from and a task I need to accomplish. Give me, as a valid JSON array, a list of the
Tool IDs that are necessary to complete this task. Return only the JSON array and no other content.

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
    packs_by_pseudo_id = {}
    pack_summaries = []
    for pack in packs:
        # The AI can get messed up with the author/repo/name Pack IDs here, so give a hashed pack ID
        pseudo_id = pack.pack_id.__hash__()
        packs_by_pseudo_id[pseudo_id] = pack.pack_id

        pack_summaries.append(
            {
                "tool_id": pseudo_id,
                "name": pack.name,
                "description": pack.description,
                "arguments": pack.run_args,
            }
        )

    tools_string = json.dumps(pack_summaries)
    prompt = TOOL_SELECTION_PROMPT.format(
        user_input=task_description, tools_string=tools_string
    )

    pseudo_ids = ask_llm(prompt, llm)

    selected_packs = []
    for pseudo_id in pseudo_ids:
        # Get the proper pack_id from the pseudo_id
        proper_id = packs_by_pseudo_id[pseudo_id]
        selected_packs.append(proper_id)

    return selected_packs


def ask_llm(prompt: str, llm: BaseChatModel):
    """Encapsulate the OpenAI specific stuff to easier support other frameworks in the future"""
    message = HumanMessage(content=prompt)

    response = llm(messages=[message])

    try:
        return json.loads(response.content)
    except JSONDecodeError as e:
        # TODO: Better handle error
        return []
