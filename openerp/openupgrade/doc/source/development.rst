Migration script development
++++++++++++++++++++++++++++

.. toctree::
   :maxdepth: 2

   devfaq

Migration Scrips consist of two main files in every module's migration directory located in the target source code:
- pre-migration.py
- post-migration.py

What they do is derived from their names, you should check the API Documentation of the openupgradelib for details of standard methods available.

The general purpose of those scripts is to manipulate directly the database entries of the source database *copy* and change them in a way so that they are compatible with the target database source code. Note, that when running Odoo's '--update-all' flag on your *target source code* but on top of your *source database*, Odoo's internal updating mechanism will use your migrating scripts to manipulate your database in a way, so that it can be start up properly on the underlying (target) source code. If this succeeds, chances are, that your scripts are working, if not, you have to go over the scripts and make a new test run on a fresh copy (@Reviewer: or is a falling migration reverted?) of your source database.

General recommendations about 'pre-migration.py' and 'post-migration.py'
---------------------------------------------------------
tbd by power-users

Note on deferred upgrades
-------------------------
In some cases, you need to defer some operations until the rest of the migration of the individual modules has terminated. The deferred_VERSION.py https://github.com/OCA/OpenUpgrade/blob/8.0/openerp/openupgrade is responsible for that. Note, that OpenUpgrade cannot see if migrations was successful so it executes this script every time regardless of success of the migration. Therefore this script must be robust against repeating execution (include checks!)
