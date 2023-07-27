import re
from typing import Callable, Union, Optional

from langchain.chat_models.base import BaseChatModel

from autopack import Pack
from autopack.get_pack import get_all_installed_packs, get_all_pack_info
from autopack.pack_config import PackConfig, InstallerStyle
from autopack.pack_response import PackResponse
from autopack.prompts import GET_MORE_TOOLS_TEMPLATE, TOOL_SELECTION_TEMPLATE
from autopack.utils import call_llm


def functions_bulleted_list(packs: list[PackResponse]) -> str:
    functions_string = []
    grouped_packs: dict[str, list[type[PackResponse]]] = {}
    for pack in packs:
        if not pack.categories:
            continue

        for category in pack.categories:
            if category not in grouped_packs:
                grouped_packs[category] = []
            grouped_packs[category].append(pack)

    for category, category_packs in grouped_packs.items():
        functions_string.append(f"\n## {category}")
        sorted_by_name = sorted(category_packs, key=lambda p: p.name)
        for pack in sorted_by_name:
            args = pack.run_args
            args_signature = ", ".join([f"{arg.get('name')}: {arg.get('type')}" for arg in args.values()])
            args_descriptions = (
                "; ".join([f"{arg.get('name')} ({arg.get('type')}): {arg.get('description')}" for arg in args.values()])
                or "None."
            )
            functions_string.append(
                f"- {pack.name}({args_signature}): {pack.description} | Arguments: {args_descriptions}"
            )

    return "\n".join(functions_string)


def select_packs_prompt(
    packs: list[Union[Pack, PackResponse]], task_description: str, function_request: Optional[str] = None
) -> str:
    """
    Generate a prompt for the pack selection process based on the task description and an optional function request.

    Args:
        packs: (list[Pack | PackResponse]): Packs to include in selection
        task_description (str): A description of the task to be used when selecting tools.
        function_request (Optional[str]): A specific type of function asked for (e.g. a `get_more_tools` function).

    Returns:
        str: A prompt that can be fed to the LLM for pack selection.
    """

    if function_request:
        return TOOL_SELECTION_TEMPLATE.format(task=task_description, functions=functions_bulleted_list(packs))

    return GET_MORE_TOOLS_TEMPLATE.format(
        task=task_description,
        functions=functions_bulleted_list(packs),
        functions_request=function_request,
    )


def select_packs(
    task_description: str,
    llm: Union[BaseChatModel, Callable],
    function_request: Optional[str] = None,
    config: PackConfig = PackConfig.global_config(),
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
        config (PackConfig): Custom config to use

    Returns:
        list[str]: A list of selected Pack IDs
    """

    if config.installer_style == InstallerStyle.manual:
        selection_pool = get_all_installed_packs()
    else:
        selection_pool = get_all_pack_info()

    prompt = select_packs_prompt(selection_pool, task_description, function_request)

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
