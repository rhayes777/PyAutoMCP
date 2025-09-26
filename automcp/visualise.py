from typing import Union

import uuid

from fastmcp import FastMCP
from mcp.server.fastmcp import Image

import autolens as al
from pathlib import Path
import autolens.plot as aplt
from automcp.pydantic_wrapper import pydantic_from_class
from automcp.resources import ProfileFinder
from autogalaxy.profiles.mass import MassProfile

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
    mcp_server.add_tool(visualise_mass_profile)


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


def _make_output():
    filename = uuid.uuid4().hex[:6]

    return aplt.Output(
        path=Path("/tmp"),
        filename=filename,
        format="png",
    )


light_profile_finder = ProfileFinder(al.LightProfile)
mass_profile_finder = ProfileFinder(MassProfile)

light_profiles = list(
    map(
        pydantic_from_class,
        light_profile_finder.all_classes,
    )
)
mass_profiles = list(
    map(
        pydantic_from_class,
        mass_profile_finder.all_classes,
    )
)

PydanticLightProfile = Union[tuple(light_profiles)]
PydanticMassProfile = Union[tuple(mass_profiles)]


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
        Reasonable values for shape_native are (50, 50) with pixel_scales of 0.02.
    title
        The title of the plot.
    """
    instance = instance.instance
    image = instance.image_2d_from(grid=grid.instance)

    output = _make_output()

    mat_plot = aplt.MatPlot2D(output=output)

    array_plotter = aplt.Array2DPlotter(
        array=image,
        mat_plot_2d=mat_plot,
    )
    array_plotter.set_title(title)
    array_plotter.figure_2d()

    return Image(path=f"/tmp/{output.filename}.png")


async def visualise_mass_profile(
    mass_profile: PydanticMassProfile,
    grid: UniformGrid2D,
    title: str = "Mass Profile Visualization",
):
    """
    Visualize a mass profile on a grid.

    Parameters
    ----------
    mass_profile
        A mass profile to visualize.
    grid
        The grid to visualize, specified as a UniformGrid2D object with shape_native and pixel_scales.
        Reasonable values for shape_native are (50, 50) with pixel_scales of 0.02.
    title
        The title of the plot.

    Returns
    -------
    Displays the deflections of the mass profile on the specified grid.
    """
    output = _make_output()

    mat_plot = aplt.MatPlot2D(output=output)

    mass_profile_plotter = aplt.MassProfilePlotter(
        mass_profile=mass_profile,
        grid=grid.instance,
        mat_plot_2d=mat_plot,
    )
    mass_profile_plotter.figures_2d(
        deflections_y=True,
        deflections_x=True,
        convergence=True,
        potential=True,
        magnification=True,
        title_suffix=title,
    )

    return Image(path=f"/tmp/{output.filename}.png")
