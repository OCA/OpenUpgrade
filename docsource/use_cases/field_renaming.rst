Field Renaming
++++++++++++++

From version 14.0 to version 15.0, in the module ``mail``, in the model
``mail.activity.type`` the html field ``default_description`` has been renamed
into ``default_note``.

Analysis
--------

.. code-block:: text

    ...
    ---Fields in module 'mail'---
    ...
    mail         / mail.activity.type       / default_description (html)    : DEL
    ...
    mail         / mail.activity.type       / default_note (html)           : NEW
    

See `Full V15 Analysis File <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/mail/15.0.1.5/upgrade_analysis.txt>`_.

Source Code Differences
-----------------------

Version 14.0
""""""""""""



.. code-block:: python

    class MailActivityType(models.Model):

        _name = 'mail.activity.type'

        default_description = fields.Html(
            string="Default Description",
            translate=True,
        )

See `Full V14 Code Source <https://github.com/odoo/odoo/blob/14.0/addons/mail/models/mail_activity.py#L80>`_.


Version 15.0
""""""""""""

.. code-block:: python

    class MailActivityType(models.Model):

        _name = 'mail.activity.type'

        default_note = fields.Html(
            string="Default Description",
            translate=True,
        )

See `Full V15 Code Source <https://github.com/odoo/odoo/blob/15.0/addons/mail/models/mail_activity_type.py#L73>`_.

Result without migration script / Expected Result
-------------------------------------------------

V14 table ``mail_activity_type``
""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "default_description"

   "1", "Email", "<p>A description</p>"
   "2", "Call", ""
   "3", "Meeting", "<p>Another description</p>"

V15 table mail_activity_type (Without migration script)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "default_note"

   "1", "Email", ""
   "2", "Call", ""
   "3", "Meeting", ""

**Problem** : the data is lost during them migration process, and the new column is empty.

V15 table mail_activity_type (With migration script)
""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "default_note"

   "1", "Email", "<p>A description</p>"
   "2", "Call", ""
   "3", "Meeting", "<p>Another description</p>"

Contribution to OpenUpgrade
---------------------------

Update ``upgrade_analysis_work.txt`` file
"""""""""""""""""""""""""""""""""""""""""

* Place side by side the two lines that correspond to the change
* Mention the operation performed, starting with ``# DONE:``

.. code-block:: text

    ---Fields in module 'mail'---
    mail         / mail.activity.type       / default_note (html)           : NEW
    mail         / mail.activity.type       / default_description (html)    : DEL
    # DONE: pre-migration, rename fields default_description -> default_note

See `Full V15 Work Analysis File <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/mail/15.0.1.5/upgrade_analysis_work.txt>`_.

Write migration Script
""""""""""""""""""""""

in the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade

    def _rename_fields(env):
        openupgrade.rename_fields(
            env,
            [
                (
                    "mail.activity.type",
                    "mail_activity_type",
                    "default_description",
                    "default_note",
                ),
            ]
        )

    @openupgrade.migrate()
    def migrate(env, version):
        _rename_fields(env)

See `Full pre migration Script <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/mail/15.0.1.5/pre-migration.py>`_.
