from fastmcp import FastMCP
import autolens as al
from pathlib import Path
import autolens.plot as aplt

import pydantic


def dataset_from_path(dataset_path: str):
    dataset_path = Path(dataset_path)
    return al.Imaging.from_fits(
        data_path=dataset_path / "data.fits",
        noise_map_path=dataset_path / "noise_map.fits",
        psf_path=dataset_path / "psf.fits",
        pixel_scales=0.1,
    )


def add(mcp_server: FastMCP):
    mcp_server.add_tool(visualize_dataset)
    mcp_server.add_tool(visualize_grid)


async def visualize_dataset(
    dataset_path: str,
):
    """
    Visualize the dataset from a given path.

    Parameters
    ----------
    dataset_path
        The path to the dataset directory containing 'data.fits', 'noise_map.fits', and 'psf.fits'.
    """
    dataset = dataset_from_path(dataset_path)
    dataset_plotter = aplt.ImagingPlotter(dataset=dataset)
    dataset_plotter.figures_2d(data=True)


class UniformGrid2D(pydantic.BaseModel):
    """
    A uniform 2D grid used for visualization in AutoLens.

    Attributes
    ----------
    shape_native : tuple
        The shape of the grid in native pixel coordinates.
    pixel_scales : float
        The scale of each pixel in arc-seconds.
    """

    shape_native: tuple[int, int]
    pixel_scales: float


async def visualize_grid(
    grid: UniformGrid2D,
    title: str = "Uniform Grid of Coordinates",
):
    """
    Visualize a uniform grid of coordinates.

    Parameters
    ----------
    grid
        The grid to visualize, specified as a UniformGrid2D object with shape_native and pixel_scales.
    title
        The title of the plot.
    """
    grid = al.Grid2D.uniform(
        shape_native=grid.shape_native,
        pixel_scales=grid.pixel_scales,
    )
    grid_plotter = aplt.Grid2DPlotter(grid=grid)
    grid_plotter.set_title(title)
    grid_plotter.figure_2d()
