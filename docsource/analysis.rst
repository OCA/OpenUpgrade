Database analysis
+++++++++++++++++

Database analysis files are hosted in `scripts` subdirectory of the
openupgrade_scripts module directory in the https://github.com/oca/openupgrade
repository.

You can create a custom set of analysis files on any set of modules between
any two versions of Odoo using the `upgrade_analysis` module that is hosted
in https://github.com/oca/server-tools.

Earlier versions
----------------

In editions earlier than 14.0, the analysis files were hosted in the forks of
Odoo at https://github.com/oca/openupgrade. The module to create the analysis
was placed in each branch of the openupgrade repository under
odoo/addons/openupgrade_records.

Contents
--------

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

   analyse
   xmlids
   format
