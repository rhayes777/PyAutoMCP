import inspect
import operator
from functools import lru_cache, reduce
from typing import Any, Annotated, Literal, get_type_hints

from pydantic import BaseModel, Field, create_model
from pydantic.config import ConfigDict

DISCRIMINATOR = "automcp_model_type"


def _freeze(obj: Any) -> Any:
    """Recursively convert obj into a hashable structure for cache keys."""
    if isinstance(obj, dict):
        # sort by key for deterministic order
        return tuple((k, _freeze(v)) for k, v in sorted(obj.items()))
    if isinstance(obj, (list, tuple)):
        return tuple(_freeze(v) for v in obj)
    if isinstance(obj, set):
        return tuple(sorted(_freeze(v) for v in obj))
    # For ConfigDict or other mappings
    try:
        # Treat like a mapping (e.g., ConfigDict behaves like dict)
        return tuple((k, _freeze(v)) for k, v in sorted(obj.items()))
    except Exception:
        return obj  # assume already hashable


@lru_cache(maxsize=None)
def _base_for_cached(cls: type, config_key: tuple) -> type:
    """
    Cached factory for a safe dynamic base.

    We reconstruct the actual `model_config` from the hashable `config_key`
    to avoid passing unhashable dicts into the cache.
    """
    # Rebuild dict from the frozen key
    model_config_kwargs = dict(
        config_key
    )  # shallow (keys/values already frozen/primitive)
    model_config_kwargs["arbitrary_types_allowed"] = True
    # Ensure arbitrary_types_allowed is always True
    model_config = ConfigDict(**model_config_kwargs)

    name = f"{cls.__name__}Base"
    if issubclass(cls, BaseModel):
        # Single inheritance to avoid duplicate BaseModel in MRO
        return type(name, (cls,), {"model_config": model_config})
    else:
        # cls first, then BaseModel — preserves cls behavior and avoids MRO conflicts
        return type(name, (cls, BaseModel), {"model_config": model_config})


def pydantic_from_class(
    cls: type,
    *,
    extra_config: dict[str, Any] | None = None,
) -> type[BaseModel]:
    """
    Build a Pydantic model from a plain Python class *cls*.

    - Subclasses *cls* so instances are also instances of the original class.
    - Adds a Literal discriminator field (name=DISCRIMINATOR) for discriminated unions.
    - Extracts field types from `__init__` annotations and defaults from the signature.
    """
    # Normalize and freeze config so it can be used as a cache key
    ec = extra_config or {}
    # Always enforce arbitrary_types_allowed=True, but allow overrides to be supplied as well
    config_key = _freeze({"arbitrary_types_allowed": True, **ec})

    DynamicBase = _base_for_cached(cls, config_key)

    # Collect fields from __init__
    sig = inspect.signature(cls.__init__)
    hints = get_type_hints(cls.__init__, include_extras=True)

    fields: dict[str, tuple[type, Any]] = {}
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        typ = hints.get(name, Any)
        default = param.default if param.default is not inspect._empty else ...
        fields[name] = (typ, default)

    # Discriminator literal is fully qualified to avoid module/name collisions
    literal_value = f"{cls.__module__}.{cls.__name__}"
    fields[DISCRIMINATOR] = (Literal[literal_value], literal_value)

    Model = create_model(
        f"{cls.__name__}Model",
        __base__=DynamicBase,
        __module__=cls.__module__,
        __doc__=cls.__doc__,
        **fields,
    )
    return Model


def make_discriminated_union(classes: list[type]):
    """
    Build Pydantic models from a list of plain classes and return:
      - models: {cls -> GeneratedModel}
      - union_type: Annotated[Union[...], Field(discriminator=DISCRIMINATOR)]
    """
    import logging

    log = logging.getLogger(__name__)
    models: dict[type, type[BaseModel]] = {}
    for c in classes:
        try:
            models[c] = pydantic_from_class(c)
        except Exception as e:
            # Keep going on individual failures (metaclass or signature oddities, etc.)
            log.warning("Skipping %s: %s", c, e)

    model_types = list(models.values())
    if not model_types:
        raise ValueError("No models could be built from the provided classes.")

    union = reduce(operator.or_, model_types[1:], model_types[0])
    return models, Annotated[union, Field(discriminator=DISCRIMINATOR)]
