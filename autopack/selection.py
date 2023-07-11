import json

from langchain.chat_models.base import BaseChatModel
from langchain.schema import SystemMessage

from autopack.api import pack_search

TOOL_SELECTION_PROMPT_TEMPLATE = """You are an autonomous AI Assistant named AutoPack. AutoPack works on behalf of another AI Assistant who will be completing tasks. AutoPack is excellent at choosing the right tools for the task. Keeping a small tool set is important, so AutoPack aims to include only the tools that are required. AutoPack has access to the following tools:
--- TOOLS ---
{tools_string}
--- END TOOLS ---
Respond with the following JSON structure:
--- FORMAT INSTRUCTIONS ---
```json
{{"tools": [{{ "tool_id": tool_id, "reason": reason_for_recommending }}] }}
```
For example, if you think tool #1234 might be necessary:
```json
{{'tools': [{{ "tool_id": 1234, "reason": "The breathe tool might be necessary because the user needs oxygen"}}]}}
```
--- END FORMAT INSTRUCTIONS ---
---- TASK ----
{user_input}
--- END TASK ---
Given the TASK, return all of the tools that are necessary to complete the task.
Begin!"""


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
    pack_summaries = ""
    for i, pack in enumerate(packs):
        # Use a number instead of a tool ID because the AI can mismatch tool names and repos
        pseudo_id = i + 1
        pack_summaries += f"""--- TOOL #{pseudo_id} ---
tool_id: {pseudo_id}
name: "{pack.name}"
description: "{pack.description}"
arguments: "{pack.run_args}"
"""

    prompt = TOOL_SELECTION_PROMPT_TEMPLATE.format(user_input=task_description, tools_string=pack_summaries)

    response = ask_llm(prompt, llm)

    tools = json.loads(response.content)
    # TODO Handle json errors, perhaps a retry

    selected_packs = []
    for selected_tool in tools.get("tools"):
        tool_index = selected_tool.get("tool_id")
        selected_packs.append(packs[tool_index - 1].pack_id)

    return selected_packs


def ask_llm(prompt: str, llm: BaseChatModel) -> list[str]:
    """Encapsulate the OpenAI specific stuff to easier support other frameworks in the future"""
    message = SystemMessage(content=prompt)

    response = llm(messages=[message])

    return response
