Model Renaming
++++++++++++++

From version 14.0 to version 15.0, in the module ``calendar``, the model
``calendar.contacts`` has been renamed into ``calendar.filters``.

Source Code Differences
-----------------------

Version 14.0
""""""""""""

.. code-block:: python

    class Contacts(models.Model):
        _name = "calendar.contacts"
        _description = "Calendar Contacts"

        user_id = fields.Many2one(
            comodel_name="res.users",
            string="Me",
            required=True,
            default=lambda self: self.env.user,
        )
        partner_id = fields.Many2one(
            comodel_name="res.partner",
            string="Employee",
            required=True,
        )
        active = fields.Boolean(string="Active", default=True)
        # ...


See `Full V14 Code Source <https://github.com/odoo/odoo/blob/68814f52e4fd44e190a2a71ee99a010a08eef674/addons/calendar/models/calendar_contact.py#LL7-L21>`_.


Version 15.0
""""""""""""

.. code-block:: python

    class Contacts(models.Model):
        _name = "calendar.filters"
        _description = "Calendar Filters"

        user_id = fields.Many2one(
            comodel_name="res.users",
            string="Me",
            required=True,
            default=lambda self: self.env.user,
        )
        partner_id = fields.Many2one(
            comodel_name="res.partner",
            string="Employee",
            required=True,
        )
        active = fields.Boolean(string="Active", default=True)
        partner_checked = fields.Boolean(string="Checked", default=True)
        # ...

See `Full V15 Code Source <https://github.com/odoo/odoo/blob/45e4be17f3f73d6e4122a43383afd774f4cbc926/addons/calendar/models/calendar_filter.py#LL7-L23>`_.

Result without migration script / Expected Result
-------------------------------------------------

V14 table ``calendar_contacts``
""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "user_id", "partner_id", "active"

   "1", "1", 34, true
   "1", "2", 52, true
   "1", "3", 22, false

V15 table ``calendar_filters`` (Without migration script)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "user_id", "partner_id", "active", "partner_checked"

   "[empty table]"


**Problem** : the data is lost during the migration process, and the new table is empty.

V15 table ``calendar_filters`` (With migration script)
""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "user_id", "partner_id", "active", "partner_checked"

   "1", "1", 34, true, true
   "1", "2", 52, true, true
   "1", "3", 22, false, true

Contribution to OpenUpgrade
---------------------------

apriori.py file
"""""""""""""""

The list of the renamed models is present in a ``apriori.py`` file in each version
of openupgrade.

* Until version 13, the file is present in this path:
  ``odoo/addons/openupgrade_records/lib/apriori.py``.

* from version 14.0 onwards, the file is present in this path:
  ``openupgrade_scripts/apriori.py``.

Add a key in the following dict:

.. code-block:: python

    renamed_models = {
        "calendar.contacts": "calendar.filters",
    }

See `Full v15 apriori file <https://github.com/OCA/OpenUpgrade/blob/97491cb7d9a8ed494a49cf1db9b7fc8852aac254/openupgrade_scripts/apriori.py#LL93-L98>`_.

**Note:**

This code is NOT used by openupgrade itself, during the migration process.
It is used to generate correctly the analysis files,
during the initialization of the Openupgrade project, for each release.

Write migration Script
""""""""""""""""""""""

in the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade

    @openupgrade.migrate()
    def migrate(env, version):
        openupgrade.rename_models(env.cr, [("calendar.contacts", "calendar.filters")])
        openupgrade.rename_tables(env.cr, [("calendar_contacts", "calendar_filters")])

See `Full pre migration Script <https://github.com/OCA/OpenUpgrade/blob/534a550faf166f2908c68327ee979411917e6c3d/openupgrade_scripts/scripts/calendar/15.0.1.1/pre-migration.py#LL3-L19>`_.
