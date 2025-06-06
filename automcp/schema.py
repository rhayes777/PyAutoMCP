from functools import cached_property
from pydantic import BaseModel

import autolens as al

import pydantic

from autoconf.dictable import from_dict


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
