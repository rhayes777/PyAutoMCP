from typing import Literal

from mcp.server import FastMCP
import autolens as al
from autoconf.dictable import to_dict
from autogalaxy.profiles.mass import MassProfile


def add(mcp: FastMCP):
    mcp.add_tool(get_profile_example)
    mcp.add_tool(get_profile_info)


class ProfileFinder:
    def __init__(self, root_cls):
        self._classes = []

        def add_class(cls):
            self._classes.append(cls)
            for subclass in cls.__subclasses__():
                add_class(subclass)

        add_class(root_cls)

    def find(self, name) -> list[type]:
        """
        Find a profile class by its name.

        Parameters
        ----------
        name : str
            The name of the profile class to find.

        Returns
        -------
        type
            The profile class if found, otherwise None.
        """
        name = name.strip().lower()
        return [cls for cls in self._classes if name in cls.__name__.lower()]

    @property
    def all_names(self) -> list[str]:
        """
        Get all profile class names.

        Returns
        -------
        list[str]
            A list of all profile class names.
        """
        return [cls.__name__ for cls in self._classes]

    @property
    def all_classes(self) -> list[type]:
        """
        Get all profile classes.

        Returns
        -------
        list[type]
            A list of all profile classes.
        """
        return self._classes


light_profile_finder = ProfileFinder(al.LightProfile)
mass_profile_finder = ProfileFinder(MassProfile)


async def get_profile_info(profile_type: Literal["light", "mass"]) -> list[dict]:
    """
    Get the names and descriptions of all available light or mass profile classes.

    Parameters
    ----------
    profile_type : str
        The type of the profile ('light' or 'mass').

    Returns
    -------
    list[str]
        A list of profile class names.
    """
    if profile_type == "light":
        finder = light_profile_finder
    elif profile_type == "mass":
        finder = mass_profile_finder
    else:
        raise ValueError("profile_type must be either 'light' or 'mass'.")

    return [
        {
            "name": cls.__name__,
            "description": cls.__doc__ or "No description available.",
        }
        for cls in finder.all_classes
    ]


async def get_profile_example(
    search_string: str,
    profile_type: Literal["light", "mass"],
) -> list[dict]:
    """
    Search for example instances of a mass or light profile based on a search string and profile type.

    It is essential to use this tool before constructing profiles, galaxies, or tracers, as it provides example
    that can be used to understand the parameters and structure of the profiles.

    Parameters
    ----------
    search_string
        A search string to filter profile names.
    profile_type : str
        The type of the profile ('light' or 'mass').

    Returns
    -------
    Examples
        A list of dictionaries representing example instances of profiles that match the search string.
    """
    if profile_type == "light":
        finder = light_profile_finder
    elif profile_type == "mass":
        finder = mass_profile_finder
    else:
        raise ValueError("profile_type must be either 'light' or 'mass'.")

    profile_classes = finder.find(search_string)

    output = []

    for profile_class in profile_classes:
        try:
            profile_instance = profile_class()
        except TypeError as e:
            # Skip classes that cannot be instantiated without arguments
            print(f"Skipping {profile_class.__name__}: {e}")
            continue
        output.append(to_dict(profile_instance))

    return output


async def get_galaxy_example() -> list[dict]:
    """
    Retrieve example instances of galaxies.

    Returns
    -------
    Examples
        A list of dictionaries representing example instances of galaxies that match the search string.
    """
    return [
        {
            "type": "instance",
            "class_path": "autogalaxy.galaxy.galaxy.Galaxy",
            "arguments": {
                "redshift": 0.5,
                "bulge": {
                    "type": "instance",
                    "class_path": "autogalaxy.profiles.light.standard.sersic.Sersic",
                    "arguments": {
                        "ell_comps": {"type": "tuple", "values": [0.0, 0.111111]},
                        "intensity": 1.0,
                        "sersic_index": 2.5,
                        "centre": {"type": "tuple", "values": [0.0, 0.0]},
                        "effective_radius": 1.0,
                    },
                },
                "disk": {
                    "type": "instance",
                    "class_path": "autogalaxy.profiles.light.standard.sersic.Sersic",
                    "arguments": {
                        "ell_comps": {"type": "tuple", "values": [0.0, 0.3]},
                        "intensity": 0.3,
                        "sersic_index": 1.0,
                        "centre": {"type": "tuple", "values": [0.0, 0.0]},
                        "effective_radius": 3.0,
                    },
                },
            },
        }
    ]


def get_tracer_example() -> list[dict]:
    """
    Retrieve example instances of tracers.

    Returns
    -------
    Examples
        A list of dictionaries representing example instances of tracers.
    """

    return [
        {
            "type": "instance",
            "class_path": "autolens.lens.tracer.Tracer",
            "arguments": {"galaxies": []},
        }
    ]
