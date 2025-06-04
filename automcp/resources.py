import json

from mcp.server import FastMCP
import autolens as al
import autofit as af
from pathlib import Path

from autoconf.dictable import to_dict, from_dict
from autogalaxy.profiles.mass import MassProfile


def add(mcp: FastMCP):
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
