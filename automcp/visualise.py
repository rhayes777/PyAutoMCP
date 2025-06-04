from fastmcp import FastMCP
import autolens as al
from pathlib import Path
import autolens.plot as aplt


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
