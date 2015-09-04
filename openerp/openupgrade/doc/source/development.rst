=========================================================
Migration script development
=========================================================

.. toctree::
   :maxdepth: 2

   devfaq

Migration Scrips consist of two (or more) main files in every module's migration directory located in the target source code:

* pre-migration.py (or pre-anythingyouwant.py)
* post-migration.py (or post-anythingyouwant.py)

What they do is derived from their names, you should check the API Documentation_ of the openupgradelib_ for details of library methods that are readily available for your migration task.

The general purpose of those scripts is to manipulate directly the database entries of the source database in order to change them in a way so that they are compatible with the target database source code. To make that happen smoothly, is your task.
When you run (TODO DOC HOWTO RUN A CUSTOM MIGRATION) a migration, Odoo's *internal* updating mechanism will be used (OpenUpgrade is providing sugar code for the migration task only). (@Experts: Under what circumstances a failing migration is reverted?)

General recommendations about 'pre-migration.py' and 'post-migration.py'
------------------------------------------------------------------------
tbd by an expert

Special Case: Module Renames and Module Merges
----------------------------------------------
tbd by an expert

Special Case: deferred upgrades
-------------------------------
In some cases, you need to defer some operations until the rest of the migration of the individual modules has terminated. The deferred_VERSION.py_ is responsible for that. Note, that OpenUpgrade cannot see if migrations was successful so it executes this script every time regardless of success of the migration. Therefore this script must be robust against repeating execution (include checks!)

.. _Documentation: https://doc.therp.nl/openupgrade/API.html
.. _openupgradelib: https://github.com/OCA/openupgradelib/releases
.. _deferred_VERSION.py: https://github.com/OCA/OpenUpgrade/blob/8.0/openerp/openupgrade
