# AutoPack

AutoPack is a Python library and CLI designed to interact with the [AutoPack repository](https://autopack.ai), a
collection of tools for AI
Agents, currently tailored for LangChain implementations.

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

## Safety and Security Notice

Please exercise caution when using the AutoPack repository and library. The repository and library are currently in the
early stages and intended for research purposes only. Ensure you review the Packs you install as they are directly
cloned from GitHub. AutoPack and its maintainers are not liable for any misuse or negligence regarding the repository
and library.

For more details, please refer to
the [Safety and Security section](https://github.com/AutoPackAI/autopack/wiki#safety-and-security-notice) in the
documentation.

## Contributing

We welcome contributions to the AutoPack ecosystem. Here are some ways you can help:

- **Create new tools!** Expand the AutoPack repository by developing and submitting your own tools. Share your ideas and
  solutions with the AutoPack community.
- **Submit GitHub repos**: If you come across GitHub repositories containing useful tools, submit them to
  the [AutoPack repository](https://autopack.ai/submissions). We'll create Packs out of the tools in those repositories
  by providing the necessary metadata.
- **Try it out for yourself**: Test AutoPack in your projects and provide feedback. Share your experiences, report bugs,
  and suggest improvements by opening issues on GitHub.
- **Contribute code**: Help improve AutoPack by opening pull requests. You can choose to work on unresolved issues or
  implement new features that you believe would enhance the functionality of the library. Please note that the AutoPack
  library is intentionally designed to be compact and straightforward.

We appreciate your contributions and look forward to your involvement in making AutoPack a vibrant and valuable resource
for the autonomous AI community.

## License

AutoPack is released under the [MIT License](https://opensource.org/licenses/MIT).