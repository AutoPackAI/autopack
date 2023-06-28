class NoopPack:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def run(self, query: str):
        return f"noop: {query}"

    async def arun(self, *args, **kwargs):
        return self.run(*args, **kwargs)
