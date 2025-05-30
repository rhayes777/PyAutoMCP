class DummyMCP:
    """
    A dummy MCP class for testing purposes.
    This class is not used in production and is only here to satisfy the type hints.
    """

    def tool(self):
        return self

    def __call__(self, func):
        return func

    def resource(self, path, name=None, description=None):
        print(path, name, description)

        def decorator(func):
            print(func())
            return func

        return decorator
