import json

from pathlib import Path
from mcp.server.fastmcp import FastMCP

import argparse

from autofit import SearchOutput
from autofit.aggregator import Aggregator

# Initialize FastMCP server
mcp = FastMCP("output_inspector")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


@mcp.tool()
async def list_searches(directory: str) -> str:
    """
    List the directories of all searches in the given directory.
    """
    aggregator = Aggregator.from_directory(Path(directory))
    return json.dumps([search.directory for search in aggregator.searches])


@mcp.tool()
async def get_model_info(directory: str) -> str:
    """
    Get a description of the model that was optimized.
    """
    with open(Path(directory) / "model.info") as f:
        return f.read()


@mcp.tool()
async def get_model_result(directory: str) -> str:
    """
    Get a description of the result of optimization.
    """
    with open(Path(directory) / "model.result") as f:
        return f.read()


# @mcp.tool()
# async def get_samples(directory: str) -> str:
#     """
#     Get the samples from the optimization.
#     """
#     search_output = SearchOutput(Path(directory))
#
#     samples = search_output.samples
#     path = Path("/tmp/samples.csv")
#     samples.write_table(path)
#
#     with open(path) as file:
#         csv_data = file.read()
#
#     path.unlink()
#
#     return csv_data


if __name__ == "__main__":
    mcp.run(transport="stdio")
