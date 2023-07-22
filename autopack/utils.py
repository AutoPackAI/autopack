import importlib
import json
import os
import re
import sys
from asyncio import iscoroutinefunction
from json import JSONDecodeError
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Union, Coroutine

from langchain.chat_models.base import BaseChatModel
from langchain.schema import SystemMessage, BaseMessage
from pydantic import BaseModel

from autopack.errors import AutoPackLoadError
from autopack.pack_response import PackResponse

if TYPE_CHECKING:
    from autopack.pack import Pack


def find_or_create_autopack_dir(depth=0) -> str:
    """Try to find a suitable .autopack directory. Tries in this order:
    1. Directory specified in environment variable AUTOPACK_DIR
    2. Existing .autopack directory in current directory
    3. Existing .autopack directory up to 3 directories up
    4. Creates an .autopack directory in current directory
    """
    env_dir = os.environ.get("AUTOPACK_DIR")
    if env_dir:
        return env_dir

    autopack_dir = os.path.abspath(os.path.join(os.getcwd(), *[os.pardir] * depth, ".autopack"))

    if not os.path.exists(autopack_dir) or not os.path.isdir(autopack_dir):
        if depth > 3:
            os.makedirs(".autopack", exist_ok=True)
            return ".autopack"
        return find_or_create_autopack_dir(depth=depth + 1)

    return autopack_dir


def load_metadata_file() -> dict[str, Any]:
    """Return the parsed contents of the metadata file, returning an empty dict if not found or otherwise failed"""
    metadata_dir = find_or_create_autopack_dir()
    metadata_file = os.path.join(metadata_dir, "pack_metadata.json")

    if not os.path.exists(metadata_file):
        return {}

    with open(metadata_file, "r") as f:
        try:
            return json.load(f)
        except JSONDecodeError:
            return {}


def write_metadata_file(data: dict[str, Any]):
    metadata_dir = find_or_create_autopack_dir()
    metadata_file = os.path.join(metadata_dir, "pack_metadata.json")

    with open(metadata_file, "w+") as f:
        json.dump(data, f)


def find_module(pack_data: PackResponse) -> ModuleType:
    autopack_dir = find_or_create_autopack_dir()
    package_path = pack_data.package_path
    pack_module_path = os.path.join(autopack_dir, extract_unique_directory_name(pack_data.repo_url))

    sys.path.insert(0, autopack_dir)
    sys.path.insert(0, pack_module_path)

    try:
        return importlib.import_module(package_path)
    finally:
        sys.path.remove(autopack_dir)
        sys.path.remove(pack_module_path)


def fetch_pack_object(pack_data: PackResponse) -> type["Pack"]:
    package_path = pack_data.package_path
    class_name = pack_data.class_name
    try:
        module = find_module(pack_data)
        pack_class = getattr(module, class_name)
        return pack_class
    except ImportError:
        raise AutoPackLoadError(
            f"Could not import module '{package_path}'. The path is incorrect or module does not exist."
        )
    except AttributeError:
        raise AutoPackLoadError(
            f"Module '{package_path}' does not contain a class named '{class_name}'. The class name is incorrect."
        )
    except TypeError:
        raise AutoPackLoadError(
            f"'{class_name}' in module '{package_path}' is not a class or cannot be instantiated without arguments."
        )


def format_packs_to_openai_functions(packs: list["Pack"]) -> list[dict[str, Any]]:
    return [format_pack_to_openai_function(pack) for pack in packs]


def format_pack_to_openai_function(pack: "Pack") -> dict[str, Any]:
    # Change this if/when other LLMs support functions
    required = []
    run_args = pack.args
    for arg_name, arg in run_args.items():
        arg_required = arg.pop("required", [])
        if arg_required:
            required.append(arg_name)
        run_args[arg_name] = arg

    return {
        "name": pack.name,
        "description": pack.description,
        "parameters": {"type": "object", "properties": run_args},
        "required": required,
    }


def run_args_from_args_schema(args_schema: type[BaseModel]) -> dict[str, dict[str, str]]:
    run_args: dict[str, Any] = {}
    if not args_schema:
        return run_args

    schema = args_schema.schema()
    if not schema:
        return run_args

    for param_name, param in schema.get("properties", []).items():
        run_args[param_name] = {
            "type": param.get("type", param.get("anyOf", "string")),
            "name": param_name,
            "description": param.get("description", ""),
            "required": param_name in schema.get("required", []),
        }
    return run_args


def functions_bulleted_list(packs: list[type["Pack"]]) -> str:
    functions_string = []
    grouped_packs: dict[str, list[type[Pack]]] = {}
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
            args: list[dict[str, str]] = []
            if pack.args_schema:
                args = list(run_args_from_args_schema(pack.args_schema).values())
            args_signature = ", ".join([f"{arg.get('name')}: {arg.get('type')}" for arg in args])
            args_descriptions = (
                "; ".join([f"{arg.get('name')} ({arg.get('type')}): {arg.get('description')}" for arg in args])
                or "None."
            )
            functions_string.append(
                f"- {pack.name}({args_signature}): {pack.description} | Arguments: {args_descriptions}"
            )

    return "\n".join(functions_string)


def functions_summary(packs: list["Pack"]) -> str:
    return ", ".join([f"{pack.name}" for pack in packs])


def extract_unique_directory_name(repo_url: str) -> str:
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    # Replace any non-alphanumeric characters with underscores
    return re.sub(r"[^a-zA-Z0-9]", "_", repo_name)


def call_llm(prompt: str, llm: Union[BaseChatModel, Callable[[str], str]]) -> str:
    """
    Call the given LLM  with the specified prompt.

    The function supports both callable LLMs and LLMs that are instances of the BaseChatModel class.

    Args:
        prompt (str): The prompt to feed to the LLM.
        llm (Union[BaseChatModel, Callable]): The LLM to call.

    Returns:
        str: The response from the LLM.
    """
    if isinstance(llm, BaseChatModel):
        message = SystemMessage(content=prompt)
        response = llm(messages=[message])
        if isinstance(response, BaseMessage):
            return response.content
        else:
            return response
    elif callable(llm):
        return llm(prompt)

    return ""


async def acall_llm(prompt: str, llm: Union[BaseChatModel, Callable[[str], str], Coroutine[Any, Any, str]]) -> str:
    """
    Asynchronously call the given LLM  with the specified prompt.

    The function supports both callable LLMs and LLMs that are instances of the BaseChatModel class.

    Args:
        prompt (str): The prompt to feed to the LLM.
        llm (Union[BaseChatModel, Awaitable[Callable]]): The LLM to call.

    Returns:
        str: The response from the LLM.
    """
    if isinstance(llm, BaseChatModel):
        message = SystemMessage(content=prompt)
        response = await llm._call_async(messages=[message])
        if isinstance(response, BaseMessage):
            return response.content
        else:
            return response
    elif callable(llm) and iscoroutinefunction(llm):
        return await llm(prompt)

    return call_llm(prompt, llm)  # type: ignore
