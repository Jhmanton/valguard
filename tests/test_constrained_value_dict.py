# ---------------------------------------------------------------------
#   Tests for Constrained Value Dict
# ---------------------------------------------------------------------


import pytest

from valguard import (
    AnyConstraint,
    ConfigurationError,
    ConstrainedValueDict,
    IntervalConstraint,
    IntValue,
    ValidationError,
)

# ---------------------------------------------------------------------
#   ConstrainedValueDict.__init__
# ---------------------------------------------------------------------


def test_valid_empty_initialisation() -> None:
    dct: ConstrainedValueDict[int, IntValue] = ConstrainedValueDict()
    assert isinstance(dct, ConstrainedValueDict)
    assert isinstance(dct.constraint, AnyConstraint)
    assert len(dct) == 0


def test_valid_initialisation_with_data() -> None:
    data = {1: IntValue(10), 2: IntValue(20)}
    cst = IntervalConstraint(0, 100)
    dct: ConstrainedValueDict[int, IntValue] = ConstrainedValueDict(cst, data)
    assert dct.constraint is cst
    assert dict(dct) == data


@pytest.mark.parametrize(
    ("constraint", "expected_type"),
    [
        (None, "NoneType"),
        ("not a constraint", "str"),
    ],
)
def test_invalid_constraint_type_raises(constraint: object, expected_type: str) -> None:
    msg = (
        f"Invalid constraint: expected instance of Constraint, "
        f"got <class '{expected_type}'>"
    )
    with pytest.raises(ConfigurationError, match=msg):
        ConstrainedValueDict(constraint)  # type: ignore[arg-type]


def test_data_fails_validation_at_construction() -> None:
    data = {1: IntValue(10), 2: IntValue(150)}
    cst = IntervalConstraint(0, 100)
    with pytest.raises(ValidationError):
        ConstrainedValueDict(cst, data)


def test_initialise_with_other_constrained_value_dict() -> None:
    original = ConstrainedValueDict[int, IntValue](
        IntervalConstraint(0, 100),
        data={1: IntValue(42), 2: IntValue(99)},
    )

    # Reuse original as input to a new instance
    copy = ConstrainedValueDict[int, IntValue](
        IntervalConstraint(0, 100),
        data=original,
    )

    assert dict(copy) == dict(original)
    assert all(isinstance(v, IntValue) for v in copy.values())


# ---------------------------------------------------------------------
#   ConstrainedValueDict.__setitem__
# ---------------------------------------------------------------------


def test_setitem_accepts_valid_value() -> None:
    dct = ConstrainedValueDict[int, IntValue](
        IntervalConstraint(0, 100),
    )
    dct[42] = IntValue(75)
    assert dct[42] == IntValue(75)


def test_setitem_rejects_constraint_violation() -> None:
    dct = ConstrainedValueDict[int, IntValue](
        IntervalConstraint(0, 50),
    )
    with pytest.raises(ValidationError, match="lies outside"):
        dct[101] = IntValue(75)


# ---------------------------------------------------------------------
#   ConstrainedValueDict general behaviour
# ---------------------------------------------------------------------


def test_basic_dict_interface_operations() -> None:
    dct = ConstrainedValueDict[int, IntValue]()

    # Insert
    dct[1] = IntValue(10)
    dct[2] = IntValue(20)

    # Get item
    assert dct[1] == IntValue(10)
    assert dct[2] == IntValue(20)

    # __len__
    assert len(dct) == 2

    # __contains__
    assert 1 in dct
    assert 3 not in dct

    # __delitem__
    del dct[1]
    assert len(dct) == 1
    assert 1 not in dct

    # __iter__
    keys = list(iter(dct))
    assert keys == [2]

    # items, keys and values
    assert list(dct.items()) == [(2, IntValue(20))]
    assert list(dct.keys()) == [2]
    assert list(dct.values()) == [IntValue(20)]


def test_update_merges_entries() -> None:
    dct = ConstrainedValueDict[int, IntValue](AnyConstraint())
    dct[1] = IntValue(10)

    dct.update({2: IntValue(20), 3: IntValue(30)})

    assert len(dct) == 3
    assert dct[2] == IntValue(20)
    assert dct[3] == IntValue(30)
