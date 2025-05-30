from automcp import aggregate, optimisation
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "autolens",
    instructions="""
The autolens server provides tools for performing non-linear optimisation to fit lens models to datasets.

When two galaxies are aligned along the line of sight, they can form a strong gravitational lensing system.
What we observe is the light from a background source galaxy being bent by the foreground lens galaxy.

We can create a model of the lensing system. This model includes light profiles for the source galaxy and mass profiles 
for the lens galaxy. It can also include light profiles for the foreground galaxy.

A model is a class with free parameters that can be optimised to fit the data. An instance is a class with fixed parameters.
Models may contain nested models or instances, allowing for complex lensing systems to be modelled.

Models and instances can be defined in JSON format, which allows for easy sharing and modification of models.
Schemas use placeholders like `<MassProfile>` and `<LightProfile>` to indicate where child JSON objects should be inserted.

For example:

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

Defines a model with a lens galaxy and a source galaxy, where the lens galaxy has a mass profile and the source galaxy 
has a light profile. The `<MassProfile>` and `<LightProfile>` placeholders should be replaced with the JSON 
representations of the specific mass and light profiles you want to use.

For example, if you want to use an IsothermalSph mass profile and an ExponentialCoreSph light profile, the JSON would 
look like this:

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
            "mass": {
              "class_path": "autogalaxy.profiles.mass.total.isothermal.IsothermalSph",
              "type": "model",
              "arguments": {
                "centre": {
                  "type": "tuple_prior",
                  "arguments": {
                    "centre_0": {
                      "lower_limit": -Infinity,
                      "upper_limit": Infinity,
                      "type": "Gaussian",
                      "id": 6,
                      "mean": 0.0,
                      "sigma": 0.1
                    },
                    "centre_1": {
                      "lower_limit": -Infinity,
                      "upper_limit": Infinity,
                      "type": "Gaussian",
                      "id": 7,
                      "mean": 0.0,
                      "sigma": 0.1
                    }
                  }
                },
                "einstein_radius": {
                  "lower_limit": 0.0,
                  "upper_limit": 8.0,
                  "type": "Uniform",
                  "id": 8
                }
              }
            }
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
            "bulge": {
              "class_path": "autogalaxy.profiles.light.linear.exponential_core.ExponentialCoreSph",
              "type": "model",
              "arguments": {
                "centre": {
                  "type": "tuple_prior",
                  "arguments": {
                    "centre_0": {
                      "lower_limit": -Infinity,
                      "upper_limit": Infinity,
                      "type": "Gaussian",
                      "id": 9,
                      "mean": 0.0,
                      "sigma": 0.3
                    },
                    "centre_1": {
                      "lower_limit": -Infinity,
                      "upper_limit": Infinity,
                      "type": "Gaussian",
                      "id": 10,
                      "mean": 0.0,
                      "sigma": 0.3
                    }
                  }
                },
                "effective_radius": {
                  "lower_limit": 0.0,
                  "upper_limit": 1.0,
                  "type": "Uniform",
                  "id": 11
                },
                "radius_break": {
                  "type": "Constant",
                  "value": 0.025
                },
                "gamma": {
                  "type": "Constant",
                  "value": 0.25
                },
                "alpha": {
                  "type": "Constant",
                  "value": 3.0
                }
              }
            }
          }
        }
      }
    }
  }
}

Example instance and model JSONs can be found in their respective component:// resources.

Parameters associated with the model maybe be given as floats or as prior dictionaries.

For example:

{
  "lower_limit": -Infinity,
  "upper_limit": Infinity,
  "type": "Gaussian",
  "id": 6,
  "mean": 0.0,
  "sigma": 0.1
}

Expresses a Gaussian prior with a mean of 0.0 and a standard deviation of 0.1. The model is allowed to have any value
between -Infinity and Infinity.

You can change the values of parameters in the model JSON you create to fit your needs.

Note that the prior JSON contains an `id` field. This is used to identify the parameter in the optimisation process.
If two parameters have the same `id`, they will be optimised together as a single parameter. For example, you could
define a model with four parameters where two have different `id`s and two have the same `id`. This would result in 
a an optimisation with three parameters.

It is ok to fix some part of the model as an instance, and leave other parts as a model. For example, you could
define a model with a lens galaxy as a model and a source galaxy as an instance. The lens galaxy would be optimised
while the source galaxy would be fixed. The result median pdf instance of the lens galaxy could then be used to
optimise the source galaxy in a subsequent optimisation.

Optimisations can take a long time to run, depending on the complexity of the model and the size of the dataset. It is
important to clarify the user's needs before running an optimisation.
""",
)

aggregate.add_tools(mcp)
optimisation.add(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
