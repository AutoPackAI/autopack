import json

from langchain.chat_models.base import BaseChatModel
from langchain.schema import SystemMessage, BaseMessage

from autopack.api import pack_search

TOOL_SELECTION_PROMPT_TEMPLATE = """Given the task and the tool list provided below, please return a JSON object identifying which tools would be most suitable for completing the task, along with reasons for each choice. The response should only include the JSON object, without any additional explanatory text.

Please provide the recommended tools in the following format:
{{"tools": [{{"tool_id": tool_id, "reason": reason_for_recommending }}]}}

Task: {user_input}

Tools List (in JSON format):
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
    for i, pack in enumerate(packs):
        # Use a number instead of a tool ID because the AI can mismatch tool names and repos
        pseudo_id = i + 1
        pack_summaries.append(
            {"tool_id": pseudo_id, "name": pack.name, "description": pack.description, "arguments": pack.run_args}
        )

    prompt = TOOL_SELECTION_PROMPT_TEMPLATE.format(user_input=task_description, tools_string=json.dumps(pack_summaries))

    response = ask_llm(prompt, llm)

    # TODO Handle json errors, perhaps a retry
    try:
        tools = json.loads(response.content)
    except json.JSONDecodeError as e:
        return []

    selected_packs = []
    for selected_tool in tools.get("tools"):
        tool_index = int(selected_tool.get("tool_id"))
        selected_packs.append(packs[tool_index - 1].pack_id)

    return selected_packs


def ask_llm(prompt: str, llm: BaseChatModel) -> BaseMessage:
    """Encapsulate the OpenAI specific stuff to easier support other frameworks in the future"""
    message = SystemMessage(content=prompt)

    response = llm(messages=[message])

    return response
