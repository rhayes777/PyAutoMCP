from typing import Literal

from mcp.server import FastMCP
import autolens as al
from autoconf.dictable import to_dict
from autogalaxy.profiles.mass import MassProfile


def add(mcp: FastMCP):
    mcp.add_tool(get_profile_example)
    mcp.add_tool(get_profile_names)


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


light_profile_finder = ProfileFinder(al.LightProfile)
mass_profile_finder = ProfileFinder(MassProfile)


async def get_profile_names(profile_type: Literal["light", "mass"]) -> list[str]:
    """
    Get the names of all available light or mass profile classes.

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

    return finder.all_names


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
