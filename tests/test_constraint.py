# ---------------------------------------------------------------------
#   Tests for Constraint and its subclasses
# ---------------------------------------------------------------------

from collections.abc import Callable

import pytest

from valguard import (
    AnyConstraint,
    BoolConstraint,
    BoolValue,
    BoundedFloatConstraint,
    BoundedIntConstraint,
    ConfigurationError,
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
    implies,
)

# -------------------------------------------------------------------------------------
#   All constraints reject non-Value types
# -------------------------------------------------------------------------------------

all_constraints: list[Constraint] = [
    AnyConstraint(),
    NumericConstraint(),
    IntConstraint(),
    BoolConstraint(),
    FloatConstraint(),
    LiteralStrConstraint(["H1", "H2A"]),
    BoundedIntConstraint(0, 100),
    BoundedFloatConstraint(0, 100),
]

non_value_inputs: list[object] = [
    "H1",  # str
    42,  # int
    3.14,  # float
    True,  # bool
    None,
    object(),
    "",
]


@pytest.mark.parametrize("constraint", all_constraints)
@pytest.mark.parametrize("bad_input", non_value_inputs)
def test_constraints_reject_non_value_inputs(
    constraint: Constraint,
    bad_input: object,
) -> None:
    with pytest.raises(ValidationError):
        constraint.validate(bad_input)


# -------------------------------------------------------------------------------------
#   Tests for Any Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        IntValue(5),
        FloatValue(2.5),
        BoolValue(True),  # noqa: FBT003
        StrValue("H1"),
    ],
)
def test_any_constraint_accepts_value_subclasses(value: Value) -> None:
    cst: AnyConstraint = AnyConstraint()
    assert cst.validate(value) == value


# -------------------------------------------------------------------------------------
#   Tests for Numeric Constraint
# -------------------------------------------------------------------------------------


def test_numeric_constraint_accepts_int_and_float() -> None:
    cst: NumericConstraint = NumericConstraint()
    val1: IntValue = IntValue(7)
    val2: FloatValue = FloatValue(3.14)
    assert cst.validate(val1) == val1
    assert cst.validate(val2) == val2


@pytest.mark.parametrize(
    "bad_value",
    [
        StrValue("H2A"),
        BoolValue(True),  # noqa: FBT003
    ],
)
def test_numeric_constraint_rejects_non_numeric(bad_value: Value) -> None:
    cst: NumericConstraint = NumericConstraint()
    with pytest.raises(ValidationError) as e:
        cst.validate(bad_value)
    assert str(e.value) == f"Invalid value: expected a numeric, got {bad_value!r}"


@pytest.mark.parametrize(
    "cls",
    [
        BoundedFloatConstraint,
        BoundedIntConstraint,
        FloatConstraint,
        IntConstraint,
        IntervalConstraint,
    ],
)
def test_numeric_constraint_subclass(cls: type) -> None:
    assert issubclass(cls, NumericConstraint)


# -------------------------------------------------------------------------------------
#   Tests for Interval Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [FloatValue(2.5), IntValue(7), FloatValue(0.0), IntValue(10)],
)
def test_interval_constraint_accepts_within_bounds(value: Value) -> None:
    cst: IntervalConstraint = IntervalConstraint(0.0, 10.0)
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    "value",
    [FloatValue(-0.1), IntValue(-1), FloatValue(10.1), IntValue(11)],
)
def test_interval_constraint_rejects_outside_bounds(value: Value) -> None:
    cst: IntervalConstraint = IntervalConstraint(0.0, 10.0)
    with pytest.raises(ValidationError):
        cst.validate(value)


@pytest.mark.parametrize(
    "value",
    [BoolValue(True), StrValue("H1")],  # noqa: FBT003
)
def test_interval_constraint_rejects_non_numeric(value: Value) -> None:
    cst: IntervalConstraint = IntervalConstraint(0.0, 10.0)
    with pytest.raises(ValidationError):
        cst.validate(value)


@pytest.mark.parametrize(
    "value",
    [FloatValue(-9.5), IntValue(-10), FloatValue(-5.0), IntValue(-6)],
)
def test_interval_constraint_accepts_within_negative_bounds(value: Value) -> None:
    cst: IntervalConstraint = IntervalConstraint(-10.0, -5.0)
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    "value",
    [FloatValue(-10.1), IntValue(-11), FloatValue(-4.9), IntValue(0)],
)
def test_interval_constraint_rejects_outside_negative_bounds(value: Value) -> None:
    cst: IntervalConstraint = IntervalConstraint(-10.0, -5.0)
    with pytest.raises(ValidationError):
        cst.validate(value)


def test_same_interval_returns_true_for_matching_bounds() -> None:
    c1: IntervalConstraint = IntervalConstraint(0.0, 10.0)
    c2: IntervalConstraint = IntervalConstraint(0.0, 10.0)
    assert c1.same_interval(c2) is True


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (IntervalConstraint(0.0, 10.0), IntervalConstraint(1.0, 10.0)),
        (IntervalConstraint(0.0, 10.0), IntervalConstraint(0.0, 9.9)),
        (IntervalConstraint(0.0, 10.0), IntervalConstraint(0.0, 11.0)),
    ],
)
def test_same_interval_returns_false_if_bounds_differ(
    a: IntervalConstraint,
    b: IntervalConstraint,
) -> None:
    assert a.same_interval(b) is False


def test_same_interval_returns_true_for_different_constraint_type() -> None:
    a = IntervalConstraint(0, 10)
    b = BoundedIntConstraint(0, 10)
    assert a.same_interval(b) is True
    assert b.same_interval(a) is True


def test_same_interval_returns_false_for_non_interval_constraint() -> None:
    a: IntervalConstraint = IntervalConstraint(0.0, 10.0)

    class DummyConstraint(Constraint):
        def validate(self, value: object) -> Value:
            return value  # type: ignore[return-value]

    b: Constraint = DummyConstraint()
    assert a.same_interval(b) is False


@pytest.mark.parametrize(
    ("lower", "upper"),
    [
        (1, 1 - 1e-10),
        (-1, -2),
        ("fred", 1),
        (1, "charlie"),
    ],
)
def test_interval_constraint_invalid(lower: float, upper: float) -> None:
    with pytest.raises(ConfigurationError):
        _ = IntervalConstraint(lower, upper)


# -------------------------------------------------------------------------------------
#   Tests for Literal String Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("literals", "value"),
    [
        (["H1", "H2A", "H2B"], StrValue("H1")),
        (["P", "F"], StrValue("P")),
        (["HD", "DI", "CR", "PA", "NN"], StrValue("DI")),
    ],
)
def test_literal_str_constraint_accepts_valid_literals(
    literals: list[str],
    value: StrValue,
) -> None:
    cst: LiteralStrConstraint = LiteralStrConstraint(literals)
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    ("literals", "value"),
    [
        (["H1", "H2A", "H2B"], StrValue("P")),
        (["P", "F"], StrValue("H1")),
        (["HD", "DI", "CR"], StrValue("PA")),
    ],
)
def test_literal_str_constraint_rejects_invalid_literals(
    literals: list[str],
    value: StrValue,
) -> None:
    cst: LiteralStrConstraint = LiteralStrConstraint(literals)
    with pytest.raises(ValidationError):
        cst.validate(value)


@pytest.mark.parametrize(
    "wrong_value",
    [
        BoolValue(True),  # noqa: FBT003
        IntValue(10),
        FloatValue(85.0),
    ],
)
def test_literal_str_constraint_rejects_wrong_value_type(
    wrong_value: Value,
) -> None:
    cst: LiteralStrConstraint = LiteralStrConstraint(["H1", "H2A"])
    with pytest.raises(ValidationError):
        cst.validate(wrong_value)


@pytest.mark.parametrize(
    "literals",
    [
        ["H1", " ", "H2A"],  # blank after stripping
        ["H1", "", "H2A"],  # empty string
        ["H1", None, "H2A"],  # not a string
        ["H1", 42, "H2A"],  # not a string
        [],  # empty
    ],
)
def test_literal_str_constraint_constructor_rejects_invalid_literals(
    literals: list[str],
) -> None:
    with pytest.raises(ConfigurationError):
        LiteralStrConstraint(literals)


def test_literal_str_constraint_deduplicates_literals() -> None:
    cst: LiteralStrConstraint = LiteralStrConstraint(["H1", "H2A", "H1", "H2A", "P"])
    assert cst.literals == frozenset(["H1", "H2A", "P"])

    # Validation still works
    assert cst.validate(StrValue("H1")) == StrValue("H1")
    assert cst.validate(StrValue("H2A")) == StrValue("H2A")
    assert cst.validate(StrValue("P")) == StrValue("P")


# -------------------------------------------------------------------------------------
#   Tests for Bool Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        BoolValue(True),  # noqa: FBT003
        BoolValue(False),  # noqa: FBT003
    ],
)
def test_bool_constraint_accepts_bool_value(value: BoolValue) -> None:
    cst: BoolConstraint = BoolConstraint()
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    "value",
    [
        IntValue(1),
        FloatValue(0.0),
        StrValue("H1"),
    ],
)
def test_bool_constraint_rejects_non_bool_values(value: Value) -> None:
    cst: BoolConstraint = BoolConstraint()
    with pytest.raises(ValidationError):
        cst.validate(value)


# -------------------------------------------------------------------------------------
#   Tests for Int Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        IntValue(0),
        IntValue(42),
        IntValue(-7),
    ],
)
def test_int_constraint_accepts_int_value(value: IntValue) -> None:
    cst: IntConstraint = IntConstraint()
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    "value",
    [
        FloatValue(1.0),
        BoolValue(True),  # noqa: FBT003
        StrValue("H1"),
    ],
)
def test_int_constraint_rejects_non_int_values(value: Value) -> None:
    cst: IntConstraint = IntConstraint()
    with pytest.raises(ValidationError):
        cst.validate(value)


# -------------------------------------------------------------------------------------
#   Tests for Bounded Int Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("lower", "upper", "value"),
    [
        (0, 100, IntValue(0)),
        (0, 100, IntValue(100)),
        (10, 20, IntValue(15)),
        (-5, 5, IntValue(0)),
    ],
)
def test_accepts_int_within_bounds(lower: int, upper: int, value: IntValue) -> None:
    cst: BoundedIntConstraint = BoundedIntConstraint(lower, upper)
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    ("lower", "upper", "value"),
    [
        (0, 10, IntValue(-1)),
        (0, 10, IntValue(11)),
        (-5, -1, IntValue(-6)),
        (-5, -1, IntValue(0)),
    ],
)
def test_rejects_int_outside_bounds(lower: int, upper: int, value: IntValue) -> None:
    cst: BoundedIntConstraint = BoundedIntConstraint(lower, upper)
    with pytest.raises(ValidationError):
        cst.validate(value)


@pytest.mark.parametrize(
    ("lower", "upper"),
    [
        (10, 0),
        (0.5, 0.1),
    ],
)
def test_raises_if_bounds_invalid(lower: float, upper: float) -> None:
    with pytest.raises(ConfigurationError):
        BoundedIntConstraint(lower, upper)


@pytest.mark.parametrize(
    "value",
    [
        FloatValue(5.0),
        BoolValue(True),  # noqa: FBT003
        StrValue("H1"),
    ],
)
def test_rejects_non_int_values(value: Value) -> None:
    cst: BoundedIntConstraint = BoundedIntConstraint(0, 10)
    with pytest.raises(ValidationError):
        cst.validate(value)


# -------------------------------------------------------------------------------------
#   Tests for Float Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        FloatValue(0.0),
        FloatValue(42.5),
        FloatValue(-7.25),
    ],
)
def test_float_constraint_accepts_float_value(value: FloatValue) -> None:
    cst: FloatConstraint = FloatConstraint()
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    "value",
    [
        IntValue(1),
        BoolValue(True),  # noqa: FBT003
        StrValue("H1"),
    ],
)
def test_float_constraint_rejects_non_float_values(value: Value) -> None:
    cst: FloatConstraint = FloatConstraint()
    with pytest.raises(ValidationError):
        cst.validate(value)


# -------------------------------------------------------------------------------------
#   Tests for Bounded Float Constraint
# -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("lower", "upper", "value"),
    [
        (0.0, 1.0, FloatValue(0.0)),
        (0.0, 1.0, FloatValue(1.0)),
        (-5.5, 5.5, FloatValue(0.0)),
        (10.1, 20.2, FloatValue(15.5)),
    ],
)
def test_accepts_float_within_bounds(
    lower: float,
    upper: float,
    value: FloatValue,
) -> None:
    cst: BoundedFloatConstraint = BoundedFloatConstraint(lower, upper)
    assert cst.validate(value) == value


@pytest.mark.parametrize(
    ("lower", "upper", "value"),
    [
        (0.0, 1.0, FloatValue(-0.1)),
        (0.0, 1.0, FloatValue(1.1)),
        (-1.0, 1.0, FloatValue(-1.5)),
        (-1.0, 1.0, FloatValue(1.5)),
    ],
)
def test_rejects_float_outside_bounds(
    lower: float,
    upper: float,
    value: FloatValue,
) -> None:
    cst: BoundedFloatConstraint = BoundedFloatConstraint(lower, upper)
    with pytest.raises(ValidationError):
        cst.validate(value)


@pytest.mark.parametrize(
    ("lower", "upper"),
    [
        (2.0, -2.0),
        (100.1, 99.9),
    ],
)
def test_bounded_float_constraint_invalid_bounds(
    lower: float,
    upper: float,
) -> None:
    with pytest.raises(ConfigurationError):
        BoundedFloatConstraint(lower, upper)


@pytest.mark.parametrize(
    "value",
    [
        IntValue(5),
        BoolValue(False),  # noqa: FBT003
        StrValue("P"),
    ],
)
def test_bounded_float_constraint_rejects_non_float_values(
    value: Value,
) -> None:
    cst: BoundedFloatConstraint = BoundedFloatConstraint(0.0, 10.0)
    with pytest.raises(ValidationError):
        cst.validate(value)


# -------------------------------------------------------------------------------------
#   Tests for Constraint Implication Logic
# -------------------------------------------------------------------------------------


non_parametric_constraint = [
    AnyConstraint,
    BoolConstraint,
    IntConstraint,
    FloatConstraint,
    NumericConstraint,
]

interval_constraint = [
    IntervalConstraint,
    BoundedIntConstraint,
    BoundedFloatConstraint,
]

literal_str_constraint = [LiteralStrConstraint]

CTC = Constraint | type[Constraint]


@pytest.mark.parametrize("a", [lambda x: x, lambda x: x()])
@pytest.mark.parametrize("b", [lambda x: x, lambda x: x()])
@pytest.mark.parametrize("c1", non_parametric_constraint)
@pytest.mark.parametrize("c2", non_parametric_constraint)
def test_non_parametric_implies(
    a: Callable[[CTC], CTC],
    b: Callable[[CTC], CTC],
    c1: type[Constraint],
    c2: type[Constraint],
) -> None:
    expect = False
    if c1 == c2:
        expect = True
    if c2 == AnyConstraint:
        expect = True
    if c1 in [IntConstraint, FloatConstraint] and c2 == NumericConstraint:
        expect = True
    assert implies(a(c1), b(c2)) is expect


@pytest.mark.parametrize("c1", interval_constraint)
@pytest.mark.parametrize("c2", interval_constraint)
def test_interval_constraint_cls_implies(
    c1: type[Constraint],
    c2: type[Constraint],
) -> None:
    expect = False
    if c1 == c2:
        expect = True
    if c2 == IntervalConstraint:
        expect = True
    assert implies(c1, c2) is expect


@pytest.mark.parametrize("b", [lambda x: x, lambda x: x()])
@pytest.mark.parametrize("c1", interval_constraint)
@pytest.mark.parametrize("c2", non_parametric_constraint)
def test_interval_constraint_cls_non_parametric_implies(
    b: Callable[[CTC], CTC],
    c1: type[Constraint],
    c2: type[Constraint],
) -> None:
    expect = False
    if c2 in [AnyConstraint, NumericConstraint]:
        expect = True
    if c1 == BoundedIntConstraint and c2 == IntConstraint:
        expect = True
    if c1 == BoundedFloatConstraint and c2 == FloatConstraint:
        expect = True
    assert implies(c1, b(c2)) is expect


@pytest.mark.parametrize("a", [lambda x: x, lambda x: x()])
@pytest.mark.parametrize("c1", non_parametric_constraint)
@pytest.mark.parametrize("c2", interval_constraint)
def test_non_parametric_interval_constraint_cls_implies(
    a: Callable[[CTC], CTC],
    c1: type[Constraint],
    c2: type[Constraint],
) -> None:
    expect = False
    assert implies(a(c1), c2) is expect


@pytest.mark.parametrize("c1", interval_constraint)
@pytest.mark.parametrize("c2", interval_constraint)
def test_interval_constraint_instance_cls_implies(
    c1: type[IntervalConstraint],
    c2: type[IntervalConstraint],
) -> None:
    expect = False
    if c1 == c2:
        expect = True
    if c2 == IntervalConstraint:
        expect = True
    assert implies(c1(0, 1), c2) is expect


@pytest.mark.parametrize("c1", interval_constraint)
@pytest.mark.parametrize("c2", interval_constraint)
def test_interval_constraint_cls_instance_implies(
    c1: type[IntervalConstraint],
    c2: type[IntervalConstraint],
) -> None:
    expect = False
    assert implies(c1, c2(0, 1)) is expect


@pytest.mark.parametrize("c1", interval_constraint)
@pytest.mark.parametrize("c2", interval_constraint)
@pytest.mark.parametrize(
    ("i1", "i2", "subset"),
    [((0, 1), (0.2, 0.8), False), ((0.2, 0.8), (0, 1), True), ((0, 1), (2, 3), False)],
)
def test_interval_constraint_instance_implies(
    c1: type[IntervalConstraint],
    c2: type[IntervalConstraint],
    i1: tuple[float, float],
    i2: tuple[float, float],
    subset: bool,
) -> None:
    expect = False
    if subset:
        if c1 == c2:
            expect = True
        if c2 == IntervalConstraint:
            expect = True
    assert implies(c1(*i1), c2(*i2)) is expect


@pytest.mark.parametrize("a", [lambda x: x, lambda x: x("P")])
@pytest.mark.parametrize("b", [lambda x: x, lambda x: x()])
@pytest.mark.parametrize("c2", non_parametric_constraint)
def test_literal_str_constraint_non_parametric_implies(
    a: Callable[[CTC], CTC],
    b: Callable[[CTC], CTC],
    c2: type[Constraint],
) -> None:
    expect = False
    if c2 == AnyConstraint:
        expect = True
    assert implies(a(LiteralStrConstraint), b(c2)) is expect


@pytest.mark.parametrize("a", [lambda x: x, lambda x: x()])
@pytest.mark.parametrize("b", [lambda x: x, lambda x: x("P")])
@pytest.mark.parametrize("c1", non_parametric_constraint)
def test_non_parametric_literal_str_constraint_implies(
    a: Callable[[CTC], CTC],
    b: Callable[[CTC], CTC],
    c1: type[Constraint],
) -> None:
    expect = False
    assert implies(a(c1), b(LiteralStrConstraint)) is expect


@pytest.mark.parametrize("a", [lambda x: x, lambda x: x("P")])
@pytest.mark.parametrize("b", [lambda x: x, lambda x: x(0, 1)])
@pytest.mark.parametrize("c2", interval_constraint)
def test_literal_str_constraint_interval_implies(
    a: Callable[[CTC], CTC],
    b: Callable[[CTC], CTC],
    c2: type[Constraint],
) -> None:
    expect = False
    assert implies(a(LiteralStrConstraint), b(c2)) is expect


@pytest.mark.parametrize("a", [lambda x: x, lambda x: x(0, 1)])
@pytest.mark.parametrize("b", [lambda x: x, lambda x: x("P")])
@pytest.mark.parametrize("c1", interval_constraint)
def test_interval_literal_str_constraint_implies(
    a: Callable[[CTC], CTC],
    b: Callable[[CTC], CTC],
    c1: type[Constraint],
) -> None:
    expect = False
    assert implies(a(c1), b(LiteralStrConstraint)) is expect


def test_literal_str_constraint_basic_implies() -> None:
    assert implies(LiteralStrConstraint, LiteralStrConstraint)
    assert implies(LiteralStrConstraint("P"), LiteralStrConstraint)
    assert not implies(LiteralStrConstraint, LiteralStrConstraint("P"))


@pytest.mark.parametrize("blank", [[""], [], ["", ""]])
def test_literal_str_constraint_does_not_accept_blank(blank: list[str]) -> None:
    with pytest.raises(ConfigurationError):
        LiteralStrConstraint(blank)


@pytest.mark.parametrize(
    ("g1", "g2", "subset"),
    [
        (["A", "B"], ["A", "B"], True),
        (["C", "D"], ["C", "D", "E"], True),
        (["C", "D", "E"], ["C", "E"], False),
    ],
)
def test_literal_str_constraint_implies(
    g1: list[str],
    g2: list[str],
    subset: bool,
) -> None:
    assert implies(LiteralStrConstraint(g1), LiteralStrConstraint(g2)) is subset
