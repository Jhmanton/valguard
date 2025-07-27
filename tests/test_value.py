# -------------------------------------------------------------------------------------
#   Tests for Value and its subclasses
# -------------------------------------------------------------------------------------

# ruff: noqa: FBT003

import pytest

from valguard import (
    BoolValue,
    FloatValue,
    IntValue,
    StrValue,
    ValidationError,
    Value,
)


@pytest.mark.parametrize(
    ("cls", "valid_input", "expected_type"),
    [
        (IntValue, 5, int),
        (FloatValue, 3.14, float),
        (BoolValue, True, bool),
        (StrValue, "H1", str),
    ],
)
def test_valid_value_construction(
    cls: type,
    valid_input: object,
    expected_type: type,
) -> None:
    v = cls(valid_input)
    assert v._value == valid_input
    assert type(v._value) is expected_type
    assert str(v) == str(valid_input)


@pytest.mark.parametrize(
    ("cls", "bad_input"),
    [
        (IntValue, 3.14),
        (FloatValue, "not-a-float"),
        (BoolValue, "True"),
        (StrValue, 100),
        (FloatValue, 1),
    ],
)
def test_invalid_value_raises(cls: type, bad_input: object) -> None:
    with pytest.raises(ValidationError, match="Invalid value"):
        cls(bad_input)


@pytest.mark.parametrize(
    "bad_value",
    [
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_float_value_rejects_non_finite(bad_value: float) -> None:
    with pytest.raises(ValidationError, match="Invalid value: expected finite float"):
        FloatValue(bad_value)


# -------------------------------------------------------------------------------------
#   Accessor Tests: to_float, value
# -------------------------------------------------------------------------------------


def test_int_value_and_to_float() -> None:
    x = IntValue(42)
    assert x.value == 42
    assert x.to_float == 42.0
    assert type(x.value) is int
    assert x.as_int == 42


def test_float_value_to_float() -> None:
    x = FloatValue(3.14)
    assert isinstance(x.to_float, float)
    assert x.to_float == 3.14
    assert x.value == 3.14
    assert type(x.value) is float
    assert x.as_float == 3.14


def test_bool_value() -> None:
    assert BoolValue(True).value is True
    assert BoolValue(False).value is False
    x = BoolValue(True)
    assert type(x.value) is bool
    assert x.value is True
    assert x.as_bool is True


def test_str_value_as_str() -> None:
    g = StrValue("H1")
    assert g.value == "H1"
    assert type(g.value) is str
    assert g.as_str == "H1"


# -------------------------------------------------------------------------------------
#   Equality (__eq__) tests
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (IntValue(42), IntValue(42), True),
        (IntValue(42), IntValue(43), False),
        (FloatValue(3.14), FloatValue(3.14), True),
        (FloatValue(3.14), FloatValue(2.71), False),
        (BoolValue(True), BoolValue(True), True),
        (BoolValue(True), BoolValue(False), False),
        (StrValue("H1"), StrValue("H1"), True),
        (StrValue("H1"), StrValue("H2A"), False),
        # different types
        (IntValue(1), FloatValue(1.0), False),
        (BoolValue(True), IntValue(1), False),
        (StrValue("P"), BoolValue(False), False),
    ],
)
def test_value_equality(a: Value, b: Value, expected: bool) -> None:
    assert (a == b) is expected


def test_value_not_equal_to_non_value() -> None:
    assert IntValue(5) != 5
    assert FloatValue(2.0) != "2.0"
    assert StrValue("H1") != object()
