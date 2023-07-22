import json

from autopack.api import pack_search


def print_search(query: str):
    matching_packs = pack_search(query)
    for pack in matching_packs:
        print("--------")
        print(f"Pack ID:      {pack.pack_id}")
        print(f"Dependencies: {', '.join(pack.dependencies)}")
        print(f"Description:  {pack.name}")
        print(f"Run Args:     {json.dumps(pack.run_args)}")
