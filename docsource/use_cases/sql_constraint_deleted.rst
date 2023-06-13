SQL Constraint Deleted
++++++++++++++++++++++

From version 14.0 to version 15.0, in the module ``bus``, the constraint
named ``bus_user_presence_unique`` on table ``bus_presence`` has been deleted.

Analysis
--------

.. code-block:: text

    ...
    ---Fields in module 'bus'---
    ...
    ---XML records in module 'bus'---
    DEL ir.model.constraint: bus.constraint_bus_presence_bus_user_presence_unique

See `Full V15 Analysis File <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/bus/15.0.1.0/upgrade_analysis.txt>`_.

Source Code Differences
-----------------------

Version 14.0
""""""""""""

.. code-block:: python

    class BusPresence(models.Model):
        _name = "bus.presence"

        _sql_constraints = [
            (
                "bus_user_presence_unique",
                "unique(user_id)",
                "A user can only have one IM status.",
            ),
        ]

See `Full V14 Code Source <https://github.com/odoo/odoo/blob/14.0/addons/bus/models/bus_presence.py#L17-L28>`_.


Version 15.0
""""""""""""

.. code-block:: python

    class BusPresence(models.Model):
        _name = "bus.presence"

See `Full V15 Code Source <https://github.com/odoo/odoo/blob/15.0/addons/bus/models/bus_presence.py#L17-L26>`_.

Contribution to OpenUpgrade
---------------------------

Update ``upgrade_analysis_work.txt`` file
"""""""""""""""""""""""""""""""""""""""""

* Mention the operation performed, starting with ``# DONE:``

.. code-block:: text

    ---Fields in module 'bus'---
    ---XML records in module 'bus'---
    DEL ir.model.constraint: bus.constraint_bus_presence_bus_user_presence_unique
    # DONE: pre-migration: deleted safely

See `Full V15 Work Analysis File <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/bus/15.0.1.0/upgrade_analysis_work.txt>`_.

Write migration Script
""""""""""""""""""""""

in the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade

    @openupgrade.migrate()
    def migrate(env, version):
        # Disappeared constraint
        openupgrade.delete_sql_constraint_safely(
            env,
            "bus",                          # Module name
            "bus_presence",                 # Table name
            "bus_user_presence_unique",     # SQL constraint name
        )

See `Full pre migration Script <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/bus/15.0.1.0/pre-migration.py>`_.
