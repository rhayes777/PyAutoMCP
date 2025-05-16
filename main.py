import sys

from autoconf.dictable import to_dict

sys.path.insert(0, "/Users/other/autolens/fit")


from typing import List

import json

from pathlib import Path
from mcp.server.fastmcp import FastMCP

from autofit import SearchOutput, AggregateImages
from autofit.aggregator import Aggregator
from autofit.aggregator.summary.aggregate_images import SubplotFit

mcp = FastMCP("output_inspector")


@mcp.tool()
async def list_searches(directory: str) -> str:
    """
    Get details of all searches in the directory.
    """
    aggregator = Aggregator.from_directory(Path(directory))
    return json.dumps(
        [
            {
                "name": search.name,
                "directory": str(search.directory),
                "instance": to_dict(search.instance),
                "log_evidence": search.samples.log_evidence,
            }
            for search in aggregator
        ]
    )


@mcp.tool()
async def get_model_details(directory: str) -> str:
    """
    Get a description of the model that was optimized.
    """
    return json.dumps(SearchOutput(Path(directory)).model.dict())


@mcp.tool()
async def get_model_result(directory: str) -> str:
    """
    Get a description of the posterior model resultant from the optimization.
    """
    with open(Path(directory) / "model.result") as f:
        return f.read()


@mcp.tool()
async def combine_images(
    filename: str,
    directories: List[str],
    image_names: List[str],
):
    """
    Combine the images from the searches into a single image.

    Parameters
    ----------
    filename
        The name of the output file.
    directories
        The directories containing the searches.
    image_names
        The names of the images to combine. Must be one or more of the following:

            Data
            DataSourceScaled
            SignalToNoiseMap
            ModelData
            LensLightModelData
            LensLightSubtractedImage
            SourceModelData
            SourcePlaneZoomed
            NormalizedResidualMap
            NormalizedResidualMapOneSigma
            ChiSquaredMap
            SourcePlaneNoZoom
    """
    aggregate = AggregateImages(
        [SearchOutput(Path(directory)) for directory in directories],
    )
    aggregate.extract_image(
        [SubplotFit[name] for name in image_names],
    ).save(filename)


# @mcp.tool()
# async def get_samples(directory: str) -> str:
#     """
#     Get the samples from the optimization.
#     """
#     search_output = SearchOutput(Path(directory))
#
#     samples = search_output.samples
#     path = Path("/tmp/samples.csv")
#     samples.write_table(path)
#
#     with open(path) as file:
#         csv_data = file.read()
#
#     path.unlink()
#
#     return csv_data


if __name__ == "__main__":
    mcp.run(transport="stdio")
