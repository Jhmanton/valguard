Constraints
===========

Constraint classes for runtime validation of `Value` instances.


Base Interface
--------------

.. autoclass:: valguard.constraints.Constraint
   :members:
   :undoc-members:
   :special-members: __str__
   :show-inheritance:

.. note::

   The :meth:`validate` method performs more than basic type checking —
   it often returns an instance of the appropriate :class:`Value` subclass,
   such as :class:`StrValue` or :class:`IntValue`.

   Autodoc may not reflect this casting behavior explicitly, so refer to
   implementation details or examples for precise return types.

Logical Helpers
---------------

.. autofunction:: valguard.constraints.implies

Generic Constraints
-------------------

.. autoclass:: valguard.constraints.AnyConstraint
   :members:
   :undoc-members:

.. autoclass:: valguard.constraints.BoolConstraint
   :members:
   :undoc-members:

.. autoclass:: valguard.constraints.IntConstraint
   :members:
   :undoc-members:

.. autoclass:: valguard.constraints.FloatConstraint
   :members:
   :undoc-members:

Numeric Constraints
-------------------

.. autoclass:: valguard.constraints.NumericConstraint
   :members:
   :undoc-members:

.. autoclass:: valguard.constraints.BoundedIntConstraint
   :members:
   :undoc-members:

.. autoclass:: valguard.constraints.BoundedFloatConstraint
   :members:
   :undoc-members:

Interval & Literal Constraints
------------------------------

.. autoclass:: valguard.constraints.IntervalConstraint
   :members:
   :undoc-members:

.. autoclass:: valguard.constraints.LiteralStrConstraint
   :members:
   :undoc-members:
