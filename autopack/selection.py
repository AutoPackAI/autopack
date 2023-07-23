import re
from typing import Callable, Union, Optional

from langchain.chat_models.base import BaseChatModel

from autopack import Pack
from autopack.get_pack import get_all_installed_packs
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

    installed_packs = get_all_installed_packs()

    if function_request:
        return TOOL_SELECTION_TEMPLATE.format(task=task_description, functions=functions_bulleted_list(installed_packs))

    return GET_MORE_TOOLS_TEMPLATE.format(
        task=task_description,
        functions=functions_bulleted_list(installed_packs),
        functions_request=function_request,
    )


def select_packs(
    task_description: str,
    llm: Union[BaseChatModel, Callable],
    function_request: Optional[str] = None,
) -> list[type[Pack]]:
    """Given a user input describing the task they wish to accomplish, return a list of Pack IDs that the given LLM
    thinks will be suitable for this task.

    This is good for a "pre-processing" step after receiving the task but before trying to solve it. This allows you
    to benefit from the wide tool selection while keeping your token usage low.

    You can then further filter, install the packs if desired, and then fetch them using get_pack().

    # TODO: Include user-provided packs into selection

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


def parse_selection_response(response: str) -> list[type[Pack]]:
    """
    Parse the response from the LLM and extract pack IDs.

    The response is split by commas and newlines, and any arguments provided in the response are removed.

    Args:
        response (str): The response from the LLM.

    Returns:
        list[str]: A list of parsed pack IDs.
    """
    pack_names = [r.split("(")[0].strip() for r in re.split(r"(?<=\w),|\n", response)]
    installed_packs = get_all_installed_packs()
    selected_packs = []
    for pack_name in pack_names:
        try:
            selected_pack = next(pack for pack in installed_packs if pack.name == pack_name)
            selected_packs.append(selected_pack)
        except StopIteration:
            # This means that the pack selected is not installed. This error should've been caught elsewhere
            continue

    return selected_packs
