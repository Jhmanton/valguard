"""Custom exceptions for the values package."""


class ValuesError(Exception):
    """Base class for all exceptions raised by the values package."""


class ValidationError(ValuesError):
    """Raised when a value fails validation.

    Typically indicates that the value has the wrong type or violates a constraint.
    """


class ConfigurationError(ValuesError):
    """Raised when an instance is misconfigured.

    For example, an interval constraint with a lower bound greater than the upper bound,
    or an invalid parameter passed to a `ConstrainedValueDict`.
    """


class ImplicitConversionError(TypeError, ValuesError):
    """Raised when implicit type conversion is attempted on a `Value` instance.

    For example, calling `bool(value)` instead of using `.value` or `.as_bool()`.
    """

    def __init__(self) -> None:
        super().__init__(
            "Implicit type conversion not permitted. Use `.value` instead.",
        )


class TypeMismatchError(ValuesError):
    """Raised when a value is accessed using an incompatible type-specific accessor.

    For example, calling `.as_int()` on a `BoolValue`.
    """

    def __init__(self) -> None:
        super().__init__("Incompatible accessor")
