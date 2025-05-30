import sys

from automcp import aggregate

sys.path.insert(0, "/Users/other/autolens/fit")

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("output_inspector")

aggregate.add_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
