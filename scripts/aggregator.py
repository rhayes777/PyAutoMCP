from automcp import aggregate
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("output_inspector")

aggregate.add_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
