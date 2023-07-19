Table Renaming
++++++++++++++

From version 14.0 to version 15.0, in the module ``mail``, the table
of the model ``mail.notification`` has been renamed from
``mail_message_res_partner_needaction_rel`` to ``mail_notification``.

Analysis
--------

For the time being, this change is not automatically detected and reported in the
``upgrade_analysis.txt`` file.

However, if the table is used as part of a many2many field, the following lines will be present.

.. code-block:: text

    ...
    ---Fields in module 'mail'---
    ...
    mail         / mail.message             / notified_partner_ids (many2many):
        table is now 'mail_notification' ('mail_message_res_partner_needaction_rel')

See `Full V15 Analysis File <https://github.com/OCA/OpenUpgrade/blob/15.0/openupgrade_scripts/scripts/mail/15.0.1.5/upgrade_analysis.txt>`_.

Source Code Differences
-----------------------

Version 14.0
""""""""""""

.. code-block:: python

    class MailNotification(models.Model):
        _name = "mail.notification"
        _table = "mail_message_res_partner_needaction_rel"

See `Full V14 Code Source <https://github.com/odoo/odoo/blob/14.0/addons/mail/models/mail_notification.py#L11-L13>`_.

Version 15.0
""""""""""""

.. code-block:: python

    class MailNotification(models.Model):
        _name = "mail.notification"
        _table = "mail_notification"

See `Full V15 Code Source <https://github.com/odoo/odoo/blob/15.0/addons/mail/models/mail_notification.py#L11-L13>`_.

Result without migration script / Expected Result
-------------------------------------------------

V14 table ``mail_message_res_partner_needaction_rel``
"""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "mail_message_id", "notification_type"

   "1", "92", "email"
   "2", "94", "sms"

V15 table ``mail_notification`` (Without migration script)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "mail_message_id", "notification_type"

   "", "", ""

**Problem** : the data is lost during the migration process.

V15 table ``mail_notification`` (With migration script)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "mail_message_id", "notification_type"

   "1", "92", "email"
   "2", "94", "sms"

Contribution to OpenUpgrade
---------------------------

Write migration Script
""""""""""""""""""""""

in the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade

    @openupgrade.migrate()
    def migrate(env, version):
        openupgrade.rename_tables(
            env.cr, [("mail_message_res_partner_needaction_rel", "mail_notification")]
        )

See `Full pre migration Script <https://github.com/OCA/OpenUpgrade/blob/b504f239cd3175ae7acc3e75d234ca3ea15f41ec/openupgrade_scripts/scripts/mail/15.0.1.5/pre-migration.py#LL52C1-L66C6>`_.

Notes
-----

* If you think the new name may already be used by an existing table,
  you can backup the table before the renaming as follows.

  .. code-block:: python

    if openupgrade.table_exists(env.cr, "mail_notification"):
        openupgrade.rename_tables(env.cr, [("mail_notification", None)])

* If the table has SQL constraints, you should drop them before the renaming

  .. code-block:: python

    openupgrade.delete_sql_constraint_safely(
        env,
        "mail",                                     # module name
        "mail_message_res_partner_needaction_rel",  # old table name
        "notification_partner_required",            # constraint name
    )
