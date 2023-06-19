import argparse

from autopack.installation import install_pack


def parse_args():
    parser = argparse.ArgumentParser(description="AutoPack CLI tool")

    subparsers = parser.add_subparsers(dest="command")
    install_parser = subparsers.add_parser("install", help="Install a pack")
    install_parser.add_argument(
        "pack", help="ID (author/repo/pack_name) of the pack to install"
    )
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
        result = install_pack(args.pack, args.force)
        if result:
            print("Installation completed")
        else:
            print("Installation failed")


if __name__ == "__main__":
    main()
