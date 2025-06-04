from fastmcp import FastMCP, Image
from PIL import Image as PILImage
from pydantic import BaseModel

import autolens as al
from pathlib import Path
import autolens.plot as aplt

import pydantic

from autoconf import cached_property
from autoconf.dictable import from_dict

import numpy as np
import matplotlib.pyplot as plt
import io
import base64


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
    mcp_server.add_tool(visualize_light_profile)


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

    model_config = {"ignored_types": (cached_property,)}

    @cached_property
    def instance(self):
        """
        Create a uniform grid based on the shape and pixel scales.
        """
        return al.Grid2D.uniform(
            shape_native=self.shape_native,
            pixel_scales=self.pixel_scales,
        )


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


class Component(BaseModel):
    type: str
    arguments: dict

    model_config = {"ignored_types": (cached_property,)}

    @cached_property
    def instance(self):
        return from_dict(
            {
                "type": self.type,
                "class_path": self.class_path,
                "arguments": self.arguments,
            }
        )


class Instance(Component):
    class_path: str
    type: str = "instance"


def array_to_base64_png(arr: np.ndarray) -> str:
    # Ensure the array is 2D or 3D with shape (H, W, 3) or (H, W, 4)
    if arr.ndim == 2:
        cmap = "gray"
    else:
        cmap = None

    # Create a PNG image in memory
    buf = io.BytesIO()
    plt.imsave(buf, arr, format="png", cmap=cmap)
    buf.seek(0)

    # Encode image as base64
    base64_png = base64.b64encode(buf.read()).decode("utf-8")
    return base64_png


async def visualize_light_profile(
    light_profile: Instance,
    grid: UniformGrid2D,
) -> Image:
    """
    Visualize a light profile.

    Parameters
    ----------
    light_profile
        An instance describing an instance of a light profile.
    grid
        The grid to visualize, specified as a UniformGrid2D object with shape_native and pixel_scales.
        Reasonable values for shape_native are (100, 100) or (200, 200) with pixel_scales of 0.1.

    Returns
    -------
    image
        An Image object containing the light profile visualized as a PNG image.
    """
    light_profile = light_profile.instance
    image = light_profile.image_2d_from(grid=grid.instance)

    buffer = io.BytesIO()
    PILImage.fromarray(image.native.array).convert("L").save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    return Image(data=img_bytes, format="png")
