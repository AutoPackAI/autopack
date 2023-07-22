import argparse

from autopack.installation import install_pack
from autopack.search import print_search


def parse_args():
    parser = argparse.ArgumentParser(description="AutoPack CLI tool")

    subparsers = parser.add_subparsers(dest="command")
    install_parser = subparsers.add_parser("install", help="Install a pack")
    install_parser.add_argument("pack", help="ID of the pack to install")

    search_parser = subparsers.add_parser("search", help="Search for packs")
    search_parser.add_argument("query", help="The search query")

    parser.add_argument(
        "-f",
        "--force",
        help="Force automatic dependency installation",
        action="store_true",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "install":
        result = install_pack(args.pack, args.force, quiet=False)
        if result:
            print("Installation completed")
        else:
            print("Installation failed")

    if args.command == "search":
        print_search(args.query)


if __name__ == "__main__":
    main()
