"""Define result types for use in assessment result manipulations.

Results are represented by subclasses of `TypedValue`, such as `IntValue` or `StrValue`.
Each subclass corresponds to a standard Python type, for example, `int` for `IntValue`
and `str` for `StrValue`. A `ValidationError` is raised at construction time if the
stored value does not have the correct type. All values are immutable once created.

A key design feature is that arguments are not coerced: `FloatValue(12)` will fail
because `12` is an integer. Instead, use `FloatValue(12.0)`. This prevents unexpected
coercions in processing pipelines.

Use `isinstance` to determine the type of a value. For example, if
`isinstance(x, IntValue)` is true, then `x.value` is guaranteed to be an int.

The `__str__` method returns a user-friendly string representation of the value.
For `FloatValue`, the output is formatted to two decimal places.

The name `Value` is provided as a convenient alias for `TypedValue[Any]`.
"""

import math
from abc import ABC

from .exceptions import ImplicitConversionError, TypeMismatchError, ValidationError

# -------------------------------------------------------------------------------------
#   Value and Typed Value
# -------------------------------------------------------------------------------------


class TypedValue[T](ABC):
    """Validate and store a value of a specific Python type.

    Subclasses must define `_type`, indicating the exact type of value accepted.
    For example, an `IntValue` subclass would define `_type = int`.

    For type-checked access, use the `as_*` properties, like `as_int` and  `as_bool`.
    """

    _type: type[T]  # Subclass to define

    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        if type(value) is not self._type:
            msg = (
                f"Invalid value: {value!r} (type {type(value).__name__}), "
                f"expected type {self._type.__name__}"
            )
            raise ValidationError(msg)
        self._value = value

    def __str__(self) -> str:
        """Return a string representation suitable for writing to a results file."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return a detailed representation for error messages."""
        return f"{self.__class__.__name__}({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypedValue):
            return NotImplemented
        return type(self) is type(other) and self._value == other._value

    def __hash__(self) -> int:
        return hash((self.__class__, self._value, self._type))

    def __bool__(self) -> bool:
        raise ImplicitConversionError

    def __int__(self) -> int:
        raise ImplicitConversionError

    def __float__(self) -> float:
        raise ImplicitConversionError

    @property
    def value(self) -> T:
        return self._value

    @property
    def as_int(self) -> int:
        raise TypeMismatchError

    @property
    def as_float(self) -> float:
        raise TypeMismatchError

    @property
    def as_bool(self) -> bool:
        raise TypeMismatchError

    @property
    def as_str(self) -> str:
        raise TypeMismatchError

    @property
    def to_float(self) -> float:
        """Convert value to float if applicable."""
        raise TypeMismatchError


# -------------------------------------------------------------------------------------
#   Numeric Values
# -------------------------------------------------------------------------------------


class _NumericValue[T: float](TypedValue[T], ABC):
    """Base class for numeric values that support conversion to float via `to_float`."""

    __slots__ = ()

    @property
    def to_float(self) -> float:
        return float(self.value)


class IntValue(_NumericValue[int]):
    """Integer value."""

    __slots__ = ()

    _type = int

    @property
    def as_int(self) -> int:
        return self.value


class FloatValue(_NumericValue[float]):
    """Float value. Formatted to two decimal places for display."""

    __slots__ = ()

    _type = float

    def __init__(self, value: float) -> None:
        super().__init__(value)
        if not math.isfinite(self.value):
            msg = f"Invalid value: expected finite float, got {self.value}"
            raise ValidationError(msg)

    def __str__(self) -> str:
        """Return a two-decimal-place string representation (for display/output)."""
        return f"{self.value:.2f}"

    def __repr__(self) -> str:
        """Return full-precision representation for debugging."""
        return f"{self.__class__.__name__}({self.value})"

    @property
    def as_float(self) -> float:
        return self.value


# -------------------------------------------------------------------------------------
#   Boolean Value
# -------------------------------------------------------------------------------------


class BoolValue(TypedValue[bool]):
    """Boolean value."""

    __slots__ = ()

    _type = bool

    @property
    def as_bool(self) -> bool:
        return self.value


# -------------------------------------------------------------------------------------
#   String Value
# -------------------------------------------------------------------------------------


class StrValue(TypedValue[str]):
    """String value."""

    __slots__ = ()

    _type = str

    @property
    def as_str(self) -> str:
        return self.value
