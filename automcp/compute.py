import numpy as np

from automcp.schema import Instance, UniformGrid2D


def add(mcp):
    mcp.add_tool(compute_deflections)


async def compute_deflections(
    instance: Instance,
    grid: UniformGrid2D,
) -> np.ndarray:
    """
    Compute the deflections of a given instance at specified grid coordinates.

    Parameters
    ----------
    instance
        A mass profile or tracer.
    grid
        A grid of coordinates where the deflections are computed.

    Returns
    -------
    np.ndarray
        An array of deflections at the specified grid coordinates.
    """
    return instance.instance.deflections_yx_2d_from(
        grid=grid.instance,
    ).array
