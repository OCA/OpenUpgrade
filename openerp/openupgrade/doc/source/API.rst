OpenUpgrade API
+++++++++++++++

You can use the following functions in your pre and post scripts.

Note that the path to the OpenUpgrade support library is different
in OpenERP 6 and OpenERP 6.1. For migration scripts that cover a
migration to OpenERP 6, please do support both paths using the
following stanza. Doing so enables the user to use your migration
script for migrating databases from OpenERP 5 to OpenERP 6.1 in one
step, provided that a migration script to 6.1 exists as well.

.. code-block:: python

   try:
        from openupgrade import openupgrade
   except ImportError:
        from openerp.openupgrade import openupgrade

.. automodule:: openupgrade
   :members:

