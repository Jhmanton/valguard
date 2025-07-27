"""Define a dictionary-like container that enforces value constraints.

This module introduces `ConstrainedValueDict`, a mutable mapping that enforces
validation on all inserted values. Each instance is associated with a `Constraint` that
governs both the expected `Value` type and the allowable values.

Validation is performed on assignment and during bulk updates. If a value fails
validation, a `ValidationError` is raised.
"""

from collections.abc import Iterator, Mapping, MutableMapping
from typing import Any

from .constraints import AnyConstraint, Constraint
from .core import TypedValue
from .exceptions import ConfigurationError

# -------------------------------------------------------------------------------------
#   Constrained Value Dict
# -------------------------------------------------------------------------------------

Value = TypedValue[Any]


class ConstrainedValueDict[K, V: Value](MutableMapping[K, V]):
    """A dictionary that stores validated `Value` instances.

    Each value inserted must satisfy the provided `Constraint` instance, which is
    responsible for checking both type and content validity.

    A mismatch between `value_type` and `constraint` may not be detected until the first
    value is inserted and validated.

    Arguments:
        constraint: The constraint that governs type and value validity.
        data: An optional initial mapping of key-value pairs to populate the dictionary.

    Raises:
        TypeError: If `data` is not a valid mapping or iterable of key-value pairs.
        ValueError: If `data` contains non-pair elements.
        ValidationError: If any value fails validation by the constraint.
        ConfigurationError: If the constraint is misconfigured or invalid.
    """

    ANY_CONSTRAINT = AnyConstraint()

    def __init__(
        self,
        constraint: Constraint = ANY_CONSTRAINT,
        data: Mapping[K, V] | None = None,
    ) -> None:
        # constraint must be an instance of Constraint
        if not isinstance(constraint, Constraint):
            msg = (
                f"Invalid constraint: expected instance of Constraint, "
                f"got {type(constraint)}"
            )
            raise ConfigurationError(msg)
        self._constraint = constraint

        self._data: dict[K, V] = {}
        if data is not None:
            self.update(data)  # Triggers validation via __setitem__

    def __setitem__(self, key: K, value: V) -> None:
        """Assign a value to the given key after validation.

        Raises:
            ValidationError: If the value fails constraint validation.
        """
        self.constraint.validate(value)
        self._data[key] = value

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __delitem__(self, key: K) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"constraint={self.constraint!r}, "
            f"data={self._data!r})"
        )

    @property
    def constraint(self) -> Constraint:
        return self._constraint
