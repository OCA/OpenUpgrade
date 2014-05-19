OpenUpgrade API
+++++++++++++++

In OpenUpgrade you can use the following functions in your pre and
post scripts. Use the following import from OpenUpgrade 6.1 on.

.. code-block:: python

   from openerp.openupgrade import openupgrade

In OpenUpgrade 5.0 and 6.0, the import is slightly different.

.. code-block:: python

   from openupgrade import openupgrade

General methods
---------------

.. automodule:: openupgrade
   :members:

Methods for OpenUpgrade 7.0
---------------------------

The following specific methods for 7.0 are available. These have been
developed to cover specific needs as per data model changes in that
release.

.. automodule:: openupgrade_70
   :members:

