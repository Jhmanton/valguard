"""valguard - Values and constraints for data processing pipelines."""

from typing import TYPE_CHECKING, Any

from .constrained_dict import ConstrainedValueDict
from .constraints import (
    AnyConstraint,
    BoolConstraint,
    BoundedFloatConstraint,
    BoundedIntConstraint,
    Constraint,
    FloatConstraint,
    IntConstraint,
    IntervalConstraint,
    LiteralStrConstraint,
    NumericConstraint,
    implies,
)
from .core import (
    BoolValue,
    FloatValue,
    IntValue,
    StrValue,
    TypedValue,
    _NumericValue,  # pyright: ignore[reportPrivateUsage]
)
from .exceptions import (
    ConfigurationError,
    ValidationError,
)

# Alias for convenience: use `Value` when the precise type is unknown or irrelevant.
if TYPE_CHECKING:
    Value = TypedValue[Any]
else:
    Value = TypedValue

# Alias for numeric values with `.value` of type `int | float` and a `.to_float` method.
if TYPE_CHECKING:
    NumericValue = _NumericValue[int | float]
else:
    NumericValue = _NumericValue

__all__ = [
    "AnyConstraint",
    "BoolConstraint",
    "BoolValue",
    "BoundedFloatConstraint",
    "BoundedIntConstraint",
    "ConfigurationError",
    "ConstrainedValueDict",
    "Constraint",
    "FloatConstraint",
    "FloatValue",
    "IntConstraint",
    "IntValue",
    "IntervalConstraint",
    "LiteralStrConstraint",
    "NumericConstraint",
    "NumericValue",
    "StrValue",
    "TypedValue",
    "ValidationError",
    "Value",
    "implies",
]
