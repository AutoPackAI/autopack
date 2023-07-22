import re
from typing import Callable, Union, Optional

from langchain.chat_models.base import BaseChatModel

from autopack.api import pack_search
from autopack.get_pack import try_get_pack
from autopack.prompts import GET_MORE_TOOLS_TEMPLATE, TOOL_SELECTION_TEMPLATE
from autopack.utils import functions_bulleted_list, call_llm


def select_packs_prompt(task_description: str, function_request: Optional[str] = None) -> str:
    """
    Generate a prompt for the pack selection process based on the task description and an optional function request.

    Args:
        task_description (str): A description of the task to be used when selecting tools.
        function_request (Optional[str]): A specific type of function asked for (e.g. a `get_more_tools` function).

    Returns:
        str: A prompt that can be fed to the LLM for pack selection.
    """

    pack_ids = [pack.pack_id for pack in pack_search("")]
    fetched_packs = [try_get_pack(pack_id) for pack_id in pack_ids]
    installed_packs = [pack for pack in fetched_packs if pack is not None]

    if function_request:
        return TOOL_SELECTION_TEMPLATE.format(task=task_description, functions=functions_bulleted_list(installed_packs))

    return GET_MORE_TOOLS_TEMPLATE.format(
        task=task_description,
        functions=functions_bulleted_list(installed_packs),
        function_request=function_request,
    )


def select_packs(
    task_description: str, llm: Union[BaseChatModel, Callable], function_request: Optional[str] = None
) -> list[str]:
    """Given a user input describing the task they wish to accomplish, return a list of Pack IDs that the given LLM
    thinks will be suitable for this task.

    This is good for a "pre-processing" step after receiving the task but before trying to solve it. This allows you
    to benefit from the wide tool selection while keeping your token usage low.

    You can then further filter, install the packs if desired, and then fetch them using get_pack().

    Args:
        task_description (str): A description of the task to be used when selecting tools
        llm (BaseChatModel): An LLM which will be used to evaluate the selection
        function_request (Optional[str]): A specific type of function asked for (e.g. a `get_more_tools` function)

    Returns:
        list[str]: A list of selected Pack IDs
    """
    prompt = select_packs_prompt(task_description, function_request)

    response = call_llm(prompt, llm)

    return parse_selection_response(response)


def parse_selection_response(response: str) -> list[str]:
    """
    Parse the response from the LLM and extract pack IDs.

    The response is split by commas and newlines, and any arguments provided in the response are removed.

    Args:
        response (str): The response from the LLM.

    Returns:
        list[str]: A list of parsed pack IDs.
    """
    return [r.split("(")[0].strip() for r in re.split(r"(?<=\w),|\n", response)]
