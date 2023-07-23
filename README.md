# AutoPack

AutoPack is a Python library and CLI designed to interact with the [AutoPack repository](https://autopack.ai)
repository, a collection of tools for AI. It is designed to be agent-neutral with a simple interface.

## Installation

You can install AutoPack using pip:

```bash
pip install autopack-tools
```

## Usage

AutoPack provides both a CLI and a Python library for interacting with the AutoPack repository.

### CLI: `autopack`

- Search for Packs: `autopack search {query}`
- Install Packs: `autopack install {Pack ID}`

### Python library: `autopack`

The `autopack` Python library allows you to work with Packs programmatically. Key functionalities include:

- Search for Packs: `pack_search(query)`
- Get a Pack: `get_pack(pack_id)`
- Get all installed Packs: `get_all_installed_packs()`
- Install a Pack: `install_pack(pack_id)`
- Select packs using an LLM: `select_packs(task_description, llm)`

For detailed examples and more information, refer to
the [AutoPack documentation](https://github.com/AutoPackAI/autopack/wiki).

## Contributing

We welcome contributions to the AutoPack ecosystem. Here are some ways you can help:

- **Create new tools!** Expand the AutoPack repository by developing and submitting your own tools. Share your ideas and
  solutions with the AutoPack community.
- **Try it out for yourself**: Test AutoPack in your projects and provide feedback. Share your experiences, report bugs,
  and suggest improvements by opening issues on GitHub.
- **Contribute code**: Help improve AutoPack by opening pull requests. You can choose to work on unresolved issues or
  implement new features that you believe would enhance the functionality of the library. Please note that the AutoPack
  library is intentionally designed to be compact and straightforward.

We appreciate your contributions and look forward to your involvement in making AutoPack a vibrant and valuable resource
for the autonomous AI community.

## License

AutoPack is released under the [MIT License](https://opensource.org/licenses/MIT).