from typing import Literal

from mcp.server import FastMCP
import autolens as al
from autoconf.dictable import to_dict
from autogalaxy.profiles.mass import MassProfile


def add(mcp: FastMCP):
    mcp.add_tool(get_profile_example)


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


light_profile_finder = ProfileFinder(al.LightProfile)
mass_profile_finder = ProfileFinder(MassProfile)


async def get_profile_example(
    search_string: str,
    profile_type: Literal["light", "mass"],
) -> list[dict]:
    """
    Search for example instances of a mass or light profile based on a search string and profile type.

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

    return [to_dict(profile_class()) for profile_class in profile_classes]
