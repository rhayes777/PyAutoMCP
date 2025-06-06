from fastmcp import FastMCP
import autolens as al
from pathlib import Path
import autolens.plot as aplt

from automcp.schema import UniformGrid2D, Instance


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
    mcp_server.add_tool(visualize_instance)


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
    grid = grid.instance
    grid_plotter = aplt.Grid2DPlotter(grid=grid)
    grid_plotter.set_title(title)
    grid_plotter.figure_2d()


async def visualize_instance(
    instance: Instance,
    grid: UniformGrid2D,
    title: str = "Light Profile Visualization",
):
    """
    Visualize a light profile, galaxy or tracer on a grid.

    Parameters
    ----------
    instance
        A Component instance containing the type and arguments for the object to visualize.
    grid
        The grid to visualize, specified as a UniformGrid2D object with shape_native and pixel_scales.
        Reasonable values for shape_native are (100, 100) or (200, 200) with pixel_scales of 0.1.
    title
        The title of the plot.
    """
    instance = instance.instance
    image = instance.image_2d_from(grid=grid.instance)

    array_plotter = aplt.Array2DPlotter(
        array=image,
    )
    array_plotter.set_title(title)
    array_plotter.figure_2d()
