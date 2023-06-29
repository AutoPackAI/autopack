import os


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

    autopack_dir = os.path.abspath(
        os.path.join(os.getcwd(), *[os.pardir] * depth, ".autopack")
    )

    if not os.path.exists(autopack_dir) or not os.path.isdir(autopack_dir):
        if depth > 3:
            os.makedirs(".autopack", exist_ok=True)
            return ".autopack"
        return find_or_create_autopack_dir(depth=depth + 1)

    return autopack_dir
