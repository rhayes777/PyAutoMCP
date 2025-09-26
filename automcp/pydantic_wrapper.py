from typing import Any, Literal, get_type_hints, Annotated
from pydantic import BaseModel, create_model, Field
from pydantic.config import ConfigDict


DISCRIMINATOR = "_automcp_model_type"


def pydantic_from_class(
    cls: type,
    *,
    extra_config: dict[str, Any] | None = None,
) -> type[BaseModel]:
    """
    Build a Pydantic model from a plain Python class *cls*.

    - Adds a Literal discriminator (default 'kind') so you can use a discriminated Union.
    - Inherits from *cls* so instances are also instances of the original class.

    Args:
        cls: The source class with type-annotated attributes.
        extra_config: Extra model_config entries (e.g., {'populate_by_name': True}).

    Returns:
        A new Pydantic model subclassing both BaseModel and *cls*.
    """
    base_name = f"{cls.__name__}Base"
    base_config = {"model_config": ConfigDict(arbitrary_types_allowed=True)}
    if extra_config:
        base_config["model_config"] = ConfigDict(
            **(extra_config | {"arbitrary_types_allowed": True})
        )
    DynamicBase = type(base_name, (BaseModel, cls), base_config)

    # 2) Collect fields from annotations on the original class
    annotations = get_type_hints(cls.__init__, include_extras=True)
    fields: dict[str, tuple[type, Any]] = {}
    for name, typ in annotations.items():
        default = getattr(cls, name, ...)
        fields[name] = (typ, default)

    literal_value = f"{cls.__module__}.{cls.__name__}"
    fields[DISCRIMINATOR] = (Literal[literal_value], literal_value)

    return create_model(
        f"{cls.__name__}Model",
        __base__=DynamicBase,
        __module__=cls.__module__,
        __doc__=cls.__doc__,
        **fields,
    )


def make_discriminated_union(
    classes: list[type],
):
    """
    Build Pydantic models from a list of plain classes and return:
      - models: {cls -> GeneratedModel}
      - union_type: Annotated[Union[...], Field(discriminator=...)]
    """
    models: dict[type, type[BaseModel]] = {}
    for cls in classes:
        models[cls] = pydantic_from_class(cls)

    union_type = Annotated[
        tuple(models.values())[0] | tuple(models.values())[1]
        if len(models) == 2
        else eval(
            " | ".join(m.__name__ for m in models.values()), models
        ),  # trick for arbitrary union
        Field(discriminator=DISCRIMINATOR),
    ]
    return union_type
