from mcp.server import FastMCP
from autoconf import conf
import autolens as al


def add_views(mcp: FastMCP):
    @mcp.resource("")
    def model_details(directory: str) -> str:
        """
        Get a description of the model that was optimized.
        """
        return conf


print(conf)
