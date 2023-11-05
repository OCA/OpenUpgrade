Migration Files
===============

For each odoo module, a **migration directory** contains the analysis of
the differences between the previous version and the current version
and the migration scripts developed to ensure the migration
of this module runs properly.

For versions 14.0 and higher
----------------------------

Migration directories are hosted in `scripts` subdirectory of the
openupgrade_scripts module directory in the https://github.com/OCA/OpenUpgrade
repository.

For example, the migration folder for migrating the `account` module
from version 13.0 to version 14.0 is located here :

https://github.com/OCA/OpenUpgrade/tree/14.0/openupgrade_scripts/scripts/account/

For versions 13.0 and below
---------------------------

Migration directories are hosted in the `migration` folder of each module
in the forks of Odoo at https://github.com/OCA/OpenUpgrade.


For example, the migration folder for migrating the `account` module
from version 12.0 to version 13.0 is located here :

https://github.com/OCA/OpenUpgrade/tree/13.0/addons/account/migrations

Non official addons
-------------------

For OCA or custom addons, migration directories are hosted in the `migration`
folder of each module.

For example, the migration folder for migrating the OCA `account_global_discount` module
from version 12.0 to version 13.0 is located here :

https://github.com/OCA/account-invoicing/tree/13.0/account_global_discount

Directory contents
------------------

The contents of the migration directory per module are:

* A file `openupgrade_analysis.txt` that contains data model changes and
  changes in the set of XML records
* A file `openupgrade_analysis_work.txt` which is a copy of the previous file,
  annotated by the developers of the migration scripts
* A file `noupdate_changes.xml` containing changes that may need to be loaded
  during module migration (after reviewing the contents of this automatically
  generated file).
* A file `pre-migration.py` (or any Python file(s) starting with `pre-`) that
  is executed by the Odoo migration manager just before the module is loaded.
* A file `post-migration.py` (or any Python file(s) starting with `post-`) that
  is executed by the Odoo migration manager right after the module was loaded.
* A file `end-migration.py` (or any Python file(s) starting with `end-`) that
  is executed by the Odoo migration manager when all modules have been
  processed.

The migration directory of the base module contains an additional file
`openupgrade_general_log.txt`. This file contains some statistics as well
as the analysis records of modules that could not be found in the target
release of Odoo anymore.

.. toctree::
   :maxdepth: 2

   format

Generate the difference analysis files
--------------------------------------

You can create a custom set of analysis files on any set of modules between
any two versions of Odoo using the `upgrade_analysis` module that is hosted
in https://github.com/oca/server-tools.
(for versions 13.0 or lower, the module is named `openupgrade_records` and is
place in each branch of the OpenUpgrade repository under
`odoo/addons/openupgrade_records` path)
