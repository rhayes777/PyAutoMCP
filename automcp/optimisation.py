import json

from mcp.server import FastMCP
import autolens as al
import autofit as af
from pathlib import Path

from autoconf.dictable import to_dict, from_dict
from autogalaxy.profiles.mass import MassProfile


def add(mcp: FastMCP):
    mcp.tool()(optimise)
    register_profiles(mcp)


def register_profiles(mcp: FastMCP):
    def register_profile(profile_class, path="component:/"):
        doc = profile_class.__doc__
        name = profile_class.__name__

        path = f"{path}/{name}"

        try:
            instance = profile_class()
            model = af.Model(profile_class)
            resource_dict = {
                "model": to_dict(model),
                "instance": to_dict(instance),
                "doc": doc,
                "name": name,
            }

            @mcp.tool(name, description=doc)
            def profile_resource():
                """
                Obtain information about the profile class, including its model and instance.
                """
                return resource_dict

        except Exception as e:
            print(f"Failed to register profile {name} at path {path}: {e}")

        for subclass in profile_class.__subclasses__():
            register_profile(subclass, path)

    register_profile(al.LightProfile)
    register_profile(MassProfile)


def _convert_dict_to_model(obj) -> af.AbstractPriorModel:
    if isinstance(obj, dict):
        collection = af.Collection()
        for key, value in obj.items():
            if isinstance(value, dict):
                collection[key] = _convert_dict_to_model(value)
            else:
                collection[key] = value
        return collection

    return obj


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
    search = af.LBFGS(name=name)
    model = _convert_dict_to_model(from_dict(model_json))

    result = search.fit(model, analysis)

    return result.paths.output_path
