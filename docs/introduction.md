# Valguard  
_Constraint-aware value types for semantic validation in Python pipelines_

**Valguard** is a lightweight framework for defining and validating values in data pipelines. It separates values from constraints. This allows a source to publish the `constraint` against which it will validate each `value`. An `implies` function can determine whether values satisfying an upstream constraint are guaranteed to satisfy a downstream constraint.


---

## Key Features

- Declarative value types
- Validators for clean pipeline integration
- Type-safe abstractions compatible with Python 3.12+

## Usage

### Values

A `Value` stores a particular kind of value. It is immutable. Different methods are provided for accessing the value depending on its type: this provides a concise way to validate type and access the value simultaneously. If `x` is not an integer then `x.as_int` will raise an exception.

To avoid raising an exception, use `isinstance()` to test the type beforehand.

A subclass of `NumericValue` will have the method `.to_float`.

```python
>>> from valguard import FloatValue, IntValue, NumericValue, BoolValue
>>> fv = FloatValue(1.0)    # Must use 1.0 and not 1
>>> iv = IntValue(1)
>>> bv = BoolValue(True)
>>> isinstance(bv,NumericValue)
False
>>> isinstance(iv,NumericValue)
True
>>> bv.as_float
Traceback (most recent call last):
    ...
valguard.exceptions.TypeMismatchError: Incompatible accessor
>>> iv.as_float
Traceback (most recent call last):
    ...
valguard.exceptions.TypeMismatchError: Incompatible accessor
>>> iv.to_float
1.0
>>> iv.as_int
1
>>> fv.as_float
1.0
>>> fv.to_float
1.0
```

### Constraints

Constraints can be placed on both type and value.

```python
>>> from valguard import IntValue, BoolValue, IntervalConstraint, NumericConstraint, IntConstraint
>>> iv = IntValue(23)
>>> bv = BoolValue(False)
>>> interval_a = IntervalConstraint(0,100)
>>> interval_b = IntervalConstraint(10,20)
>>> interval_a.validate(iv)
IntValue(23)
>>> interval_b.validate(iv)
Traceback (most recent call last):
    ...
valguard.exceptions.ValidationError: Invalid value: 23.0 lies outside [10.0, 20.0]
>>> interval_a.validate(bv)
Traceback (most recent call last):
    ...
valguard.exceptions.ValidationError: Invalid value: expected a numeric, got BoolValue(False)
>>> IntConstraint().validate(iv)
IntValue(23)
>>> IntConstraint().validate(iv).as_int
23
>>> NumericConstraint().validate(iv).to_float
23.0
>>> NumericConstraint().validate(bv).to_float
Traceback (most recent call last):
    ...
valguard.exceptions.ValidationError: Invalid value: expected a numeric, got BoolValue(False)
```

#### The `implies` function

The `implies` function determines whether one constraint implies another constraint. Constraint A implies constraint B if every value that satisfies A will also satisfy B.

```python
>>> from valguard import BoundedIntConstraint, NumericConstraint, FloatConstraint, implies
>>> interval_A = BoundedIntConstraint(0,100)
>>> interval_B = BoundedIntConstraint(20,80)
>>> implies(interval_A, interval_B)
False
>>> implies(interval_B, interval_A)
True
>>> implies(interval_A, FloatConstraint)
False
>>> implies(interval_A, NumericConstraint)
True
>>> implies(NumericConstraint, interval_A)
False
```

Constraints that are parametrised (such as `IntervalConstraint` and `LiteralStrConstraint`) can be used in two ways: as an instance with specific parameters, or as a class. When used as a class, `implies` behaves differently depending on whether the class appears as the first or second argument to `implies`. As the first argument, `implies(class, B)` is True if **all** instances of `class` would imply `B`. As the second argument, `implies(A, class)` is True if **at least one** instance of `class` would be implied by `A`. For non-parametrised classes, there is no difference whether a class or an instance is used.

### Constrained Value Dictionary

A `ConstrainedValueDict` behaves like a dictionary but its values are validated against a constraint at the time of insertion.

It is intentional that no type casting is performed, not even from `int` to `IntValue`.

```python
>>> from valguard import IntValue, IntConstraint, ConstrainedValueDict
>>> d = ConstrainedValueDict(IntConstraint())                             
>>> d["one"] = IntValue(1)
>>> d["one"]
IntValue(1)
>>> d["two"] = 2
Traceback (most recent call last):
    ...
valguard.exceptions.ValidationError: Invalid value: expected an integer, got 2
```

## Installation

```bash
pip install valguard
```