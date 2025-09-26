from pathlib import Path

from automcp import optimisation, resources, visualise, compute
from mcp.server.fastmcp import FastMCP

system_dir = Path(__file__).parent / "system"

mcp = FastMCP(
    "autolens",
    instructions=(system_dir / "general.txt").read_text(encoding="utf-8"),
)

# aggregate.add_tools(mcp)
# optimisation.add(mcp)
# resources.add(mcp)
visualise.add(mcp)
compute.add(mcp)
