"""Constraints on `Value` instances.

This module defines the `Constraint` interface and its subclasses, which validate
`Value` instances according to type and semantic rules.

Overview:
    Constraints encapsulate both the expected type of a value and any additional
    semantic restrictions it must satisfy. This eliminates the need to separately
    check the type of a `Value` before validating its content.

    While `Value` subclasses ensure that their internal data is well-formed and
    strongly typed, they do not, on their own, enforce domain-specific constraints
    such as value ranges, membership in a set, or compatibility with a marking
    scheme. These concerns are handled by `Constraint` subclasses.

Validation:
    Each subclass of `Constraint` validates an object starting with a type check, to
    ensure the object is an instance of a specific `Value` subclass, and then applies
    additional rules such as bounding intervals or allowed categories.

    A `Value` instance can be validated against a `Constraint` at any time using the
    `validate()` method. If the validation fails, a `ValidationError` is raised.

Type Casting:
    >>> value: TypedValue[Any] = ...   # obtained from external source
    >>> int_value = IntConstraint().validate(value)
    `int_value` is of type IntValue

Composite Constraints:
    Constraints may internally combine multiple checks. For example, a bounded integer
    constraint may ensure that the value is an integer and lies within a specific range.
    These are represented as a single `Constraint` instance and validated together.

Type Inspection:
    You can use `isinstance()` to determine the type of a constraint, even when it
    represents a composition of simpler conditions.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from .core import (
    BoolValue,
    FloatValue,
    IntValue,
    StrValue,
    TypedValue,
    _NumericValue,
)
from .exceptions import ConfigurationError, ValidationError

# -------------------------------------------------------------------------------------
#   Constraint
# -------------------------------------------------------------------------------------

Value = TypedValue[Any]
NumericValue = _NumericValue[int | float]


def ensure_value_type[V: Value](value: object, cls: type[V], expected: str) -> V:
    if not isinstance(value, cls):
        msg = f"Invalid value: expected {expected}, got {value!r}"
        raise ValidationError(msg)
    return value


class Constraint(ABC):
    """Represents a constraint that may be imposed on a `Value`."""

    _is_parametrised = False

    @abstractmethod
    def validate(self, value: object) -> Value:
        """Validate the given `value`, or raise a `ValidationError`.

        Args:
            value: The `Value` instance to be validated.

        Returns:
            A type-cast version of the original `value`.

        Raises:
            ValidationError: If the value violates the constraint.
        """

    def __str__(self) -> str:
        """Return a string representation of the constraint."""
        return self.__class__.__name__

    def __repr__(self) -> str:
        return str(self)


class AnyConstraint(Constraint):
    """A constraint that accepts any `Value` instance without additional checks.

    This constraint enforces only that the input is an instance of `Value`, but imposes
    no further semantic restrictions.
    """

    def validate(self, value: object) -> Value:
        return ensure_value_type(value, TypedValue, "a Value instance")


class NumericConstraint(AnyConstraint):
    """Constrains a value to be numeric (an integer or float)."""

    def validate(self, value: object) -> NumericValue:
        return ensure_value_type(value, _NumericValue, "a numeric")


class IntervalConstraint(NumericConstraint):
    """Constrains a numeric value to lie in a closed interval."""

    _is_parametrised = True

    def __init__(self, lower: float, upper: float) -> None:
        try:
            self._lower = float(lower)
            self._upper = float(upper)
        except (TypeError, ValueError) as e:
            msg = f"Invalid bounds: expected float, got {lower!r}, {upper!r}"
            raise ConfigurationError(msg) from e
        if self._lower > self._upper:
            msg = f"Invalid bounds: {self._lower} > {self._upper}"
            raise ConfigurationError(msg)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.lower}, {self.upper}]"

    def validate(self, value: object) -> NumericValue:
        numeric_value = super().validate(value)
        if not (self.lower <= numeric_value.to_float <= self.upper):
            msg = (
                f"Invalid value: {numeric_value.to_float} lies outside "
                f"[{self.lower}, {self.upper}]"
            )
            raise ValidationError(msg)
        return numeric_value

    def same_interval(self, other: Constraint) -> bool:
        return (
            isinstance(other, IntervalConstraint)
            and self.lower == other.lower
            and self.upper == other.upper
        )

    @property
    def lower(self) -> float:
        return self._lower

    @property
    def upper(self) -> float:
        return self._upper


class LiteralStrConstraint(AnyConstraint):
    """Constrains a string to lie within a chosen set of possibilities."""

    _is_parametrised = True

    def __init__(self, literals: Sequence[str]) -> None:
        if not all(g and type(g) is str and g == g.strip() for g in literals):
            msg = f"Invalid literals: expected strings, got {literals!r}"
            raise ConfigurationError(msg)
        if len(literals) == 0:
            msg = "Invalid literals: cannot be empty"
            raise ConfigurationError(msg)
        self._literals = frozenset(literals)

    def __str__(self) -> str:
        return f"LiteralStrConstraint({self.literals_as_repr_string})"

    def validate(self, value: object) -> StrValue:
        str_value = ensure_value_type(value, StrValue, "a string")
        if str_value.value not in self.literals:
            msg = (
                f"Invalid literal: {value!s} not in {{{self.literals_as_repr_string}}}"
            )
            raise ValidationError(msg)
        return str_value

    @property
    def literals(self) -> frozenset[str]:
        return self._literals

    @property
    def literals_as_repr_string(self) -> str:
        return ", ".join([repr(s) for s in sorted(self.literals)])


class BoolConstraint(AnyConstraint):
    """Constrains a value to be a boolean."""

    def validate(self, value: object) -> BoolValue:
        return ensure_value_type(value, BoolValue, "a boolean")


class IntConstraint(NumericConstraint):
    """Constrains a value to be an integer."""

    def validate(self, value: object) -> IntValue:
        return ensure_value_type(value, IntValue, "an integer")


class FloatConstraint(NumericConstraint):
    """Constrains a value to be a float."""

    def validate(self, value: object) -> FloatValue:
        return ensure_value_type(value, FloatValue, "a float")


class BoundedIntConstraint(IntervalConstraint, IntConstraint):
    """Constrains a value to be an integer in a closed numeric interval.

    This combines the checks of `IntConstraint` and `IntervalConstraint`.
    """

    def validate(self, value: object) -> IntValue:
        int_value = IntConstraint.validate(self, value)
        IntervalConstraint.validate(self, int_value)
        return int_value


class BoundedFloatConstraint(IntervalConstraint, FloatConstraint):
    """Constrains a value to be an integer in a closed numeric interval.

    This combines the checks of `IntConstraint` and `IntervalConstraint`.
    """

    def validate(self, value: object) -> FloatValue:
        float_value = FloatConstraint.validate(self, value)
        IntervalConstraint.validate(self, float_value)
        return float_value


# -------------------------------------------------------------------------------------
#   Constraint implication logic
# -------------------------------------------------------------------------------------


def _implies_for_intervals(a: IntervalConstraint, b: IntervalConstraint) -> bool:
    # A necessary condition is for some instance of a to imply b
    if not isinstance(a, type(b)):
        return False
    # Comes down to checking intervals
    return b.lower <= a.lower and a.upper <= b.upper


def _implies_for_literals(a: LiteralStrConstraint, b: LiteralStrConstraint) -> bool:
    # Comes down to checking the literals
    return a.literals <= b.literals


def implies(a: Constraint | type[Constraint], b: Constraint | type[Constraint]) -> bool:
    """Returns True if `a` implies `b`.

    If constraint `a` implies constraint `b` then if a value satisfies constraint `a`,
    it is guaranteed to also satisfy constraint `b`.

    A class implies another constraint if every instance of that class implies the
    constraint. A constraint implies a class if it implies at least one instance of that
    class. And a class implies a class if each instance of the first class implies at
    least one instance of the second class.
    """
    cls_a = a if isinstance(a, type) else type(a)
    cls_b = b if isinstance(b, type) else type(b)

    # Unless an instance is parametrised, promote to its class
    if (a is not cls_a) and not a._is_parametrised:  # noqa: SLF001
        a = cls_a
    if (b is not cls_b) and not b._is_parametrised:  # noqa: SLF001
        b = cls_b

    # An interval or literal constraint implies a class iff every such constraint
    # implies that class
    if b is cls_b:
        return issubclass(cls_a, cls_b)

    # No interval constraint nor literal constraint can be implied by a class
    if a is cls_a:
        return False

    # Deal with interval constraints
    if isinstance(a, IntervalConstraint) and isinstance(b, IntervalConstraint):
        return _implies_for_intervals(a, b)

    # Deal with literal constraints
    if isinstance(a, LiteralStrConstraint) and isinstance(b, LiteralStrConstraint):
        return _implies_for_literals(a, b)

    # Interval constraints do not imply literal constraints, or vice versa
    return False
