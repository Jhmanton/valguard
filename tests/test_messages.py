from typing import Any

import pytest

from valguard import (
    AnyConstraint,
    BoolConstraint,
    BoolValue,
    BoundedFloatConstraint,
    BoundedIntConstraint,
    ConfigurationError,
    ConstrainedValueDict,
    Constraint,
    FloatConstraint,
    FloatValue,
    IntConstraint,
    IntervalConstraint,
    IntValue,
    LiteralStrConstraint,
    NumericConstraint,
    StrValue,
    ValidationError,
    Value,
)
from valguard.constraints import ensure_value_type
from valguard.core import TypedValue
from valguard.exceptions import ImplicitConversionError, TypeMismatchError

# ---------------------------------------------------------------------
# __str__ and __repr__ for Value subclasses
# ---------------------------------------------------------------------


def test_int_value_str_and_repr() -> None:
    v = IntValue(42)
    assert str(v) == "42"
    assert repr(v) == "IntValue(42)"


def test_float_value_str_and_repr() -> None:
    val = FloatValue(12.3456)
    assert str(val) == "12.35"
    assert repr(val) == "FloatValue(12.3456)"


def test_bool_value_str_and_repr() -> None:
    v = BoolValue(True)  # noqa: FBT003
    assert str(v) == "True"
    assert repr(v) == "BoolValue(True)"


def test_literal_value_str_and_repr() -> None:
    v = StrValue("H1")
    assert str(v) == "H1"
    assert repr(v) == "StrValue('H1')"


# ---------------------------------------------------------------------
# __str__ and __repr__ for Constraint subclasses
# ---------------------------------------------------------------------


def test_any_constraint_str_and_repr() -> None:
    c = AnyConstraint()
    assert str(c) == "AnyConstraint"
    assert repr(c) == "AnyConstraint"


def test_numeric_constraint_str_and_repr() -> None:
    c = NumericConstraint()
    assert str(c) == "NumericConstraint"
    assert repr(c) == "NumericConstraint"


def test_interval_constraint_str_and_repr() -> None:
    c = IntervalConstraint(0, 100)
    assert str(c) == "IntervalConstraint[0.0, 100.0]"
    assert repr(c) == "IntervalConstraint[0.0, 100.0]"


def test_literal_str_constraint_str_and_repr() -> None:
    c = LiteralStrConstraint(["H2B", "H1", "H2A"])
    assert str(c) == "LiteralStrConstraint('H1', 'H2A', 'H2B')"
    assert repr(c) == "LiteralStrConstraint('H1', 'H2A', 'H2B')"


def test_bool_constraint_str_and_repr() -> None:
    c = BoolConstraint()
    assert str(c) == "BoolConstraint"
    assert repr(c) == "BoolConstraint"


def test_int_constraint_str_and_repr() -> None:
    c = IntConstraint()
    assert str(c) == "IntConstraint"
    assert repr(c) == "IntConstraint"


def test_bounded_int_constraint_str_and_repr() -> None:
    c = BoundedIntConstraint(0, 100)
    assert str(c) == "BoundedIntConstraint[0.0, 100.0]"
    assert repr(c) == "BoundedIntConstraint[0.0, 100.0]"


# ---------------------------------------------------------------------
# __str__ and __repr__ for Constrained Value Dict
# ---------------------------------------------------------------------


def test_constrained_value_dict_str_and_repr() -> None:
    d = ConstrainedValueDict[str, IntValue](IntervalConstraint(0, 100))
    d["s1"] = IntValue(25)
    d["s2"] = IntValue(75)

    expected = (
        "ConstrainedValueDict("
        "constraint=IntervalConstraint[0.0, 100.0], "
        "data={'s1': IntValue(25), 's2': IntValue(75)})"
    )

    assert repr(d) == expected
    assert str(d) == expected


# ---------------------------------------------------------------------
# Exceptions raised by Value subclasses
# ---------------------------------------------------------------------


def test_typed_value_type_error() -> None:
    with pytest.raises(ValidationError) as e:
        IntValue("not an int")  # type: ignore[arg-type]
    assert str(e.value) == "Invalid value: 'not an int' (type str), expected type int"


def test_float_value_requires_finite() -> None:
    with pytest.raises(ValidationError) as e:
        FloatValue(float("inf"))
    assert str(e.value) == "Invalid value: expected finite float, got inf"


# ---------------------------------------------------------------------
# Exceptions raised by Constraint subclasses
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("constraint", "invalid_value", "expected_msg"),
    [
        (
            AnyConstraint(),
            "not a value",
            "Invalid value: expected a Value instance, got 'not a value'",
        ),
        (
            NumericConstraint(),
            StrValue("H1"),
            "Invalid value: expected a numeric, got StrValue('H1')",
        ),
        (
            BoolConstraint(),
            StrValue("H1"),
            "Invalid value: expected a boolean, got StrValue('H1')",
        ),
        (
            IntConstraint(),
            FloatValue(3.0),
            "Invalid value: expected an integer, got FloatValue(3.0)",
        ),
        (
            BoundedIntConstraint(0, 10),
            FloatValue(3.0),
            "Invalid value: expected an integer, got FloatValue(3.0)",
        ),
        (
            FloatConstraint(),
            IntValue(3),
            "Invalid value: expected a float, got IntValue(3)",
        ),
        (
            BoundedFloatConstraint(0.0, 1.0),
            IntValue(1),
            "Invalid value: expected a float, got IntValue(1)",
        ),
    ],
)
def test_constraint_type_errors(
    constraint: Constraint,
    invalid_value: object,
    expected_msg: str,
) -> None:
    with pytest.raises(ValidationError) as e:
        constraint.validate(invalid_value)
    assert str(e.value) == expected_msg


@pytest.mark.parametrize(
    ("constraint", "value", "expected_msg"),
    [
        (
            BoundedIntConstraint(0, 10),
            IntValue(99),
            "Invalid value: 99.0 lies outside [0.0, 10.0]",
        ),
        (
            BoundedFloatConstraint(0.0, 1.0),
            FloatValue(1.5),
            "Invalid value: 1.5 lies outside [0.0, 1.0]",
        ),
    ],
)
def test_bounded_constraint_bounds_error(
    constraint: Constraint,
    value: Value,
    expected_msg: str,
) -> None:
    with pytest.raises(ValidationError) as e:
        constraint.validate(value)
    assert str(e.value) == expected_msg


# ---------------------------------------------------------------------
# Tests that check configuration and custom validation logic
# ---------------------------------------------------------------------


def test_ensure_value_type_error_message() -> None:
    val = FloatValue(3.567)
    with pytest.raises(ValidationError) as e:
        ensure_value_type(val, IntValue, "XYZ")
    assert str(e.value) == "Invalid value: expected XYZ, got FloatValue(3.567)"


def test_interval_constraint_invalid_bounds_type() -> None:
    with pytest.raises(ConfigurationError) as e:
        IntervalConstraint("low", "high")  # type: ignore[arg-type]
    assert str(e.value) == "Invalid bounds: expected float, got 'low', 'high'"


def test_interval_constraint_inverted_bounds() -> None:
    with pytest.raises(ConfigurationError) as e:
        IntervalConstraint(100, 0)
    assert str(e.value) == "Invalid bounds: 100.0 > 0.0"


def test_literal_constraint_invalid_literals_error_message() -> None:
    with pytest.raises(ConfigurationError) as e:
        LiteralStrConstraint(["H1", " H2A", None])  # type: ignore[list-item]
    assert (
        str(e.value) == "Invalid literals: expected strings, got ['H1', ' H2A', None]"
    )


def test_literal_constraint_validation_error() -> None:
    constraint = LiteralStrConstraint(["H1", "H2A", "H2B"])
    with pytest.raises(ValidationError) as e:
        constraint.validate(StrValue("Fail"))
    assert str(e.value) == "Invalid literal: Fail not in {'H1', 'H2A', 'H2B'}"


# ---------------------------------------------------------------------
# Exceptions raised by Constrained Value Dict
# ---------------------------------------------------------------------


def test_constrained_dict_invalid_constraint_type() -> None:
    with pytest.raises(ConfigurationError) as e:
        ConstrainedValueDict[Any, IntValue](object())  # type: ignore[arg-type]
    assert (
        str(e.value)
        == "Invalid constraint: expected instance of Constraint, got <class 'object'>"
    )


def test_constrained_dict_setitem_constraint_error() -> None:
    d = ConstrainedValueDict[Any, IntValue](IntervalConstraint(0, 50))
    with pytest.raises(ValidationError) as e:
        d["a"] = IntValue(70)
    assert str(e.value) == "Invalid value: 70.0 lies outside [0.0, 50.0]"


# ---------------------------------------------------------------------
# Exceptions raised by __bool__, __int__ and __float__
# ---------------------------------------------------------------------

# Sample values for each class
SAMPLE_VALUES = {
    BoolValue: True,
    IntValue: 123,
    FloatValue: 4.56,
    StrValue: "H1",
}


@pytest.mark.parametrize(("cls", "value"), list(SAMPLE_VALUES.items()))
@pytest.mark.parametrize("method_name", ["__bool__", "__int__", "__float__"])
def test_implicit_conversion_error_message(
    cls: type,
    value: object,
    method_name: str,
) -> None:
    instance = cls(value)
    method = getattr(instance, method_name)

    with pytest.raises(ImplicitConversionError) as exc_info:
        method()

    expected = "Implicit type conversion not permitted. Use `.value` instead."
    assert str(exc_info.value) == expected


# ---------------------------------------------------------------------
# Exceptions raised by as_* accessors on incompatible types
# ---------------------------------------------------------------------


ALL_SUBCLASSES = list(SAMPLE_VALUES)

# Mapping from class to valid accessor name(s)
VALID_ACCESSORS = {
    BoolValue: {"as_bool"},
    IntValue: {"as_int"},
    FloatValue: {"as_float"},
    StrValue: {"as_str"},
}


ACCESSOR_NAMES = ["as_bool", "as_int", "as_float", "as_str"]


@pytest.mark.parametrize("cls", ALL_SUBCLASSES)
@pytest.mark.parametrize("accessor_name", ACCESSOR_NAMES)
def test_type_mismatch_error_message(
    cls: type[TypedValue[Any]],
    accessor_name: str,
) -> None:
    if accessor_name in VALID_ACCESSORS[cls]:
        # accessor is valid and should not raise
        return

    value = SAMPLE_VALUES[cls]
    instance = cls(value)

    with pytest.raises(TypeMismatchError) as exc_info:
        getattr(instance, accessor_name)

    expected = "Incompatible accessor"
    assert str(exc_info.value) == expected
