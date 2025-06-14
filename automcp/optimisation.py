import json

from mcp.server import FastMCP
import autolens as al
import autofit as af
from pathlib import Path

from autoconf.dictable import from_dict


def add(mcp: FastMCP):
    mcp.tool()(optimise)


def add_type(model_dict):
    if isinstance(model_dict, dict):
        if "type" not in model_dict:
            return {
                "type": "collection",
                "arguments": {
                    key: add_type(value) for key, value in model_dict.items()
                },
            }
    elif isinstance(model_dict, list):
        return [add_type(item) for item in model_dict]

    return model_dict


async def optimise(
    name: str,
    dataset_path: str,
    model_json: dict,
) -> str:
    """
    Run a non-linear optimisation on the given dataset using the model specified in the JSON file.

    Parameters
    ----------
    name
        The name of the optimisation task.
    dataset_path
        The path to a directory containing the dataset files.
    model_json
        A JSON describing the model to be used for optimisation.

    Returns
    -------
    The directory where the optimisation results are stored.
    """
    dataset_path = Path(dataset_path)
    dataset = al.Imaging.from_fits(
        data_path=dataset_path / "data.fits",
        noise_map_path=dataset_path / "noise_map.fits",
        psf_path=dataset_path / "psf.fits",
        pixel_scales=0.1,
    )

    analysis = al.AnalysisImaging(dataset=dataset)
    search = af.LBFGS(name=name, path_prefix="mcp")
    model = from_dict(add_type(model_json))

    result = search.fit(model, analysis)

    return result.paths.output_path
