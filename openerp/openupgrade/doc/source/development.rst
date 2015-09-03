Migration script development
++++++++++++++++++++++++++++

.. toctree::
   :maxdepth: 2

   devfaq

Migration Scrips consist of two main files in every module's migration directory located in the target sourcecode:
- pre-migration.py
- post-migration.py

What they do is derived from their names, you should check the API Documentation of the openupgradelib for details of standard methods available.

The general purpose of those scirpts is to manipulate directly the database entries of the source database *copy* and change them in a way so that they are compatible with the target database sourcecode. Note, that when runnung Odoo's '--update-all' flag on your *target sourcecode* but on top of your *source database*, Odoo's internal updating mechanism will use your migrating scripts to manipulate your database in a way, so that it can be start up properly on the underlying (target) sourcecode. If this succeeds, chances are, that your scripts are working, if not, you have to go over the scripts and make a new testrun on a freah copy (@Reviewer: or is a faling migration reverted?) of your source database.

General recommendations about 'pre-migration.py' and 'post-migration.py'
---------------------------------------------------------
tbd by power-users

Note on deffered upgrades
-------------------------
In some cases, you need to deferr some operations until the rest of the migration of the individual modules has terminated. The deferred_VERSION.py https://github.com/OCA/OpenUpgrade/blob/8.0/openerp/openupgrade is responsible for that. Note, that OpenUpgrade cannot see if migrations was sucessfull so it executes this script every time regardless of sucess of the migration. Therefore this script must be robust against repeting execution (include checks!)

