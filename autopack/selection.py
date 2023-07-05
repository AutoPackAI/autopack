import json

from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage, SystemMessage

from autopack.api import pack_search

TOOL_SELECTION_PROMPT_TEMPLATE = """You are an autonomous AI Assistant named AutoPack.

AutoPack is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, AutoPack is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

AutoPack is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, AutoPack is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, AutoPack is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, AutoPack is here to assist.

AutoPack has access to the following tools:
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

I am a human user who needs you to accomplish a task.
First, I need you to narrow down the available tools to the ones that may be necessary to complete the following task.

---- TASK ----
{user_input}
--- END TASK ---

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
        pack_summaries += f"""--- START TOOL #{pseudo_id} ---
tool_id: {pseudo_id}
name: "{pack.name}"
description: "{pack.description}"
arguments: "{pack.run_args}"
--- END TOOL #{pseudo_id} ---
"""

    prompt = TOOL_SELECTION_PROMPT_TEMPLATE.format(
        user_input=task_description, tools_string=pack_summaries
    )

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
