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
When you run a migration_, basically Odoo's *internal* updating mechanism will be used (OpenUpgrade is providing sugar code for the migration task only). 
Expert Note: Unlike a plain Odoo upgrade, OpenUpgrade only commits after each individual module upgrade. If a migration script fails, the transaction in which that module migration is run will be rolled back. The migration process can then be restarted by running `odoo.py` only with the `-d` argument for the database (i.e. without `--update all`). However, there are some technical subtleties that prevent a continued migration without manual intervention in the database.

General recommendations about 'pre-migration.py' and 'post-migration.py'
------------------------------------------------------------------------
TODO

Special Case: Module Renames and Module Merges
----------------------------------------------
In a normal case, you should be able to include your module name changes into the apriori.py_ which is automatically loaded at this_ point. However, in the case you only want to migrate a specific module, things are slightly more complicated (doc improvements via PR welcome):
 1. In order for a module to be recognized for update, it must be formally installed. In targe source code, you need to fool the server by copying the newmodule and change it's name to old folder (which presumably is not present any more in your target source code). Additioanly, delete the migrations directory in the copied folder.
 2. You then need to establish a dependency of this old name, depending on the new name. You can do that in the `[openupgrade]` stanza of the odoo config file with the `autoinstall` option.
 3. In the migration scripts, which live in your newname folder, put the those_ lines (pre-script).

Special Case: deferred upgrades
-------------------------------
In some cases, you need to defer some operations until the rest of the migration of the individual modules has terminated. The deferred_80.py_ is responsible for that. Note, that OpenUpgrade at that point_ cannot see if migrations was successful so it executes this script every time regardless of success of the migration. Therefore this script must be robust against repeating execution (include checks!)

.. _migration: https://doc.therp.nl/openupgrade/intro.html#migrating-your-database
.. _Documentation: API.rst
.. _openupgradelib: https://github.com/OCA/openupgradelib/releases
.. _deferred_80.py: https://github.com/OCA/OpenUpgrade/blob/8.0/openerp/openupgrade
.. apriori.py_: https://github.com/OCA/OpenUpgrade/blob/e2726bff62cf5929f028fe3922f80a664f129179/openerp/addons/openupgrade_records/lib/apriori.py
.. _this: https://github.com/OCA/OpenUpgrade/blame/e2726bff62cf5929f028fe3922f80a664f129179/openerp/addons/base/migrations/8.0.1.3/pre-migration.py#L37-L39
.. _point: https://github.com/OCA/OpenUpgrade/blame/0a4814e0bf849e2b1f96b998f7271ae52e5cd8c5/openerp/modules/loading.py#L427-L429
.. _those: https://github.com/OCA/OpenUpgrade/blame/e2726bff62cf5929f028fe3922f80a664f129179/openerp/addons/base/migrations/8.0.1.3/pre-migration.py#L37-L39
