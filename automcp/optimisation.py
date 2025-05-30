import json

from mcp.server import FastMCP
import autolens as al
import autofit as af
from pathlib import Path

from autoconf.dictable import from_json, to_dict
from autogalaxy.profiles.mass import MassProfile


def add(mcp: FastMCP):
    mcp.tool()(optimise)
    register_profiles(mcp)


def register_profiles(mcp: FastMCP):
    def register_profile(profile_class, path="component:/"):
        doc = profile_class.__doc__
        name = profile_class.__name__

        path = f"{path}/{name}"

        @mcp.resource(path, name=name, description=doc)
        def profile_resource():
            instance = profile_class()
            model = af.Model(profile_class)

            return json.dumps(
                {
                    "model": to_dict(model),
                    "instance": to_dict(instance),
                    "doc": doc,
                    "name": name,
                }
            )

        for subclass in profile_class.__subclasses__():
            register_profile(subclass, path)

    register_profile(al.LightProfile)
    register_profile(MassProfile)


async def optimise(
    name: str,
    dataset_path: str,
    model_json: str,
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
    search = af.LBFGS(name=name)
    model = from_json(model_json)

    result = search.fit(model, analysis)

    return result.paths.output_path
