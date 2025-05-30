from mcp.server import FastMCP
import autolens as al
import autofit as af
from pathlib import Path

from autoconf.dictable import from_json


def add(mcp: FastMCP):
    mcp.tool()(optimise)
    mcp.resource("model_json")


async def optimise(name: str, dataset_path: str, model_json: str) -> str:
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


def model_schema():
    return """
    The model is a collection of galaxies, each with a lens and source galaxy. 
    The lens galaxy has a mass profile, and the source galaxy has a light profile.
    
    The schema below describes how to construct a model JSON for a simple lensing system with a single lens galaxy 
    and a single source galaxy.
    
    <MassProfile> and <LightProfile> should be replaced with the JSON representations of specific mass and light 
    profile classes you want to use, such as `PowerLaw`, `Isothermal`, `Sersic`, etc.
    
    {
      "type": "collection",
      "arguments": {
        "galaxies": {
          "type": "collection",
          "arguments": {
            "lens": {
              "class_path": "autogalaxy.galaxy.galaxy.Galaxy",
              "type": "model",
              "arguments": {
                "redshift": {
                  "type": "Constant",
                  "value": 0.5
                },
                "mass": <MassProfile>,
              }
            },
            "source": {
              "class_path": "autogalaxy.galaxy.galaxy.Galaxy",
              "type": "model",
              "arguments": {
                "redshift": {
                  "type": "Constant",
                  "value": 1.0
                },
                "bulge": <LightProfile>,
              }
            }
          }
        }
      }
    }
    """
