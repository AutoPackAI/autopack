# AutoPack Tools

[AutoPack](https://autopack.ai) is a repository for tools that are specifically designed for AI Agents.

The `autopack-tools` Python package is designed to facilitate the installation and usage of tools hosted in the AutoPack
repository. Tools in AutoPack are called Packs.

## Note

This is still in the alpha stage. It's roughly at MVP level, and things will not work, features aren't complete, and
things will change. Be forewarned.

## Installation

Install the `autopack-tools` package from PyPI using pip:

```bash
pip install autopack-tools
```

Or Poetry:

```bash
poetry add autopack-tools
```

## Usage

### Pack IDs

Each pack in the AutoPack repository is identified by a fully qualified path based on its GitHub repository. This format
ensures uniqueness, prevents namespace collisions, and allows for easy identification of the source code location.
Importantly, it enables us to uniquely refer to a pack while keeping pack names intuitive and understandable for an LLM.

For example, the ID of a pack named `web_search` hosted in the GitHub repository `erik-megarad/my_packs` would be:

`erik-megarad/my_packs/web_search`

This format allows us to use the pack's name, `web_search`, within an Agent, making it convenient and straightforward
to reference the desired tool.

### Manual Tool Installation

You can manually install a pack using the following command:

```bash
autopack install author/repo_name/tool_name
```

### Using with LangChain

To use a tool with LangChain, you can retrieve it using the `get_pack` function from the `autopack` module:

```python
from autopack import get_pack

tool = get_pack("author/repo_name/pack_name")

# Add the tool to the 'packs' argument when instantiating your AgentExecutor
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=[tool()])
```

### Using with Auto-GPT

We are actively working on improving the integration with Auto-GPT. Stay tuned for updates!

To use `autopack` with Auto-GPT, you can edit the file `autogpt/main.py` and add `autopack` to the `COMMAND_CATEGORIES`
list.

## TODOs

This project is still in its early stages, and there are several features and enhancements that need to be implemented.
If you are interested and willing to contribute, the following list provides a good starting point:

- Tool search functionality within the CLI
- Tool search capability from Python
- Optional automatic pack installation in the `get_pack` function
- Tools for Agents to independently search for, install, and utilize other Tools
- Tool for utilizing the pack selection API of the AutoPack repository
- Optional contribution of feedback back to the AutoPack repository

## Development

For information on how to contribute to AutoPack, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file.

Feel free to modify this README to provide more specific details about your project and its functionalities.