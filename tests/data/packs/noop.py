class NoopPack:
    def run(*args, **kwargs):
        return "noop"

    async def arun(*args, **kwargs):
        return "noop"
