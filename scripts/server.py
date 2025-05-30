from automcp import aggregate, optimisation
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("automcp")

aggregate.add_tools(mcp)
optimisation.add(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
