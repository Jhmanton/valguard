Values
======


Base Class
----------

.. autoclass:: valguard.core.TypedValue
   :members:
   :special-members: __str__, __repr__
   :undoc-members:
   :show-inheritance:

.. note::

   While :class:`TypedValue` is the base class for all constraint-aware value wrappers,
   a generic alias is available for convenience:

   .. code-block:: python

      Value = TypedValue[Any]

   Use ``Value`` for type annotations when the specific constraint is either irrelevant or varies across use cases.
   For runtime checks, prefer:

   .. code-block:: python

      isinstance(obj, TypedValue)



Concrete Value Types
--------------------

.. autoclass:: valguard.core.IntValue
   :members:
   :undoc-members:

.. autoclass:: valguard.core.FloatValue
   :members:
   :undoc-members:

.. autoclass:: valguard.core.BoolValue
   :members:
   :undoc-members:

.. autoclass:: valguard.core._NumericValue
   :members:
   :undoc-members:

.. autoclass:: valguard.core.StrValue
   :members:
   :undoc-members:
