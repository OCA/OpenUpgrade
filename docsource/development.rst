Migration script development
++++++++++++++++++++++++++++

Overview
--------

The execution of the migration scripts is triggered by the "Migration Manager":
:doc:`migrationmanager`.

As explained with more detail in the page :doc:`migrationmanager`, the migration scripts
of a module are usually the combination of 3 python files (might be less if some
steps are not necessary):

- pre-migration.py
- post-migration.py
- end-migration.py

Since version 14, these files can be found here:

``openupgrade_scripts/scripts/<module-name>``

Each of those files will contain a function `migrate` which is called by the
Migration Manager.

Then, the function migrate will call other functions. Each of these functions
will execute a task of the migration, these functions are the one which
needs most of the work from developers. These functions are usually declared in the
same file.

Luckily, many pre-existing functions already exist within `openupgradelib` reducing
significantly the work of development.
See `OpenUpgrade API <https://oca.github.io/OpenUpgrade/API.html>`_

For many modules, a developer will not even need to write any function, but will
"simply" need to call pre-existing functions from `openupgradelib` with the appropriate
arguments. The main complexities becomes to learn what are the functions available in
`openupgradelib` and then to select appropriatly the arguments (usually according to
the `openupgrade_analysis.txt`, see below).

For instance, the migration to version 13 of mass_mailing did not require any custom
function: https://github.com/OCA/OpenUpgrade/pull/2273/files

After this introduction, which highlight how simple the migration scripts can be,
do not underestimate the power of OpenUpgrade.
The migration of the account module to version 13 is the kind of situation where
the full power of OpenUpgrade was unleashed to successfully overcome the
"acc-pocalypse":
https://github.com/OCA/OpenUpgrade/pull/2275/files.


Handling of the renaming and merging of custom modules with a Custom Configuration File
---------------------------------------------------------------------------------------

To handle custom code, you can create a custom configuration file
(ex: ``openupgrade-15.conf``) which can be part of your custom repo.

This file can be used to store the renaming and merge of custom modules.
The expected content structure of the file is the following:

.. code-block:: text

  [renamed_modules]
  old_module_name_1=new_module_name_1
  old_module_name_2=new_module_name_2
  [merged_modules]
  merged_module_1=new_module_merged_1

Then, you must declare this custom configuration file into your Odoo
configuration file (``odoo.cfg`` or ``odoo.conf``) like this:

.. code-block:: text

    [openupgrade]
    config_path=../config/openupgrade-15.conf

The purpose of using a configurable path is to allow you adding the openupgrade
custom configuration file into the repo where your custom modules are so you can commit
it.

When running the upgrade, the configurations ``renamed_modules`` and ``merged_modules``
will be taken into account as one of the first step of the migration as part of the
pre-migration script of the module ``base``:

.. code-block:: python

    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)



Learn from existing migration scrips
------------------------------------


Since version 14, the migration scripts are located in:

``openupgrade_scripts/scripts/<module-name>``

During the review for a given module, you can follow this process:

- Review the analysis (read more in :doc:`analysis`). First the file
  `openupgrade_analysis.txt` showing some differences between the 2 versions of
  the module. Then, `openupgrade_analysis_work.txt` to see what the developer
  planned to do.
- Then you can check the other files to see how the plan was achieved.

You should pick modules with which you are familiar with in both version and for which
you are aware of the changes.

Learn from code review of open PRs
----------------------------------

https://github.com/OCA/OpenUpgrade/pulls

This will engage you in a discussion with other contributors and help you understand
how developers selected one way or another to implement the migration scripts.

The Trial and error process for the development of your scripts
---------------------------------------------------------------

Basically, this is the happening during the step when you try to run the upgrade
described in :doc:`migration_details`:

- [A] get the copy of your database in old version as `db-upgrade`, it is
  easy to do through the database manager of your old odoo
  `http://localhost:8069/web/database/manager`
- [B] run ``odoo -d db-upgrade -u all --stop-after-init``
- [C] In case of error, fix the error adding or editing migration
  scripts within the module to fix, then rerun with ``-u <fixed_module>``
  instead of ``-u all``.
  This way of running is only done for testing purposes and will help you
  save a lot of time in the development process.
  Whenever facing unexpected errors, you might want to restart from [A] as
  this step will leave your database in an inconsistent state.
- [D] After all issues are fixed go back to ``--update all`` to ensure that all
  dependent modules have been upgraded.

Restart the upgrade of the failed module instead of upgrading all systematically
................................................................................

**As an alternative to the step [C] mentioned above...**

In case of error, fix the error (adding or editing migration
scripts), then rerun **without** the ``--update all``:
``odoo -d db-upgrade --stop-after-init``. This will continue the upgrade
process from where it left off, starting with the module that caused the
error. That way, the migration will not run the end-migration scripts of
the modules that were already upgraded before the error. But in case of a
live migration you always need to restore the database.

Note that for the time being, this is not available in all versions
(see explanations here: https://github.com/OCA/OpenUpgrade/pull/2499).
It is available only for 12 and 13:
https://github.com/OCA/OpenUpgrade/pulls?q=is%3Apr+%5BFIX%5D+reset+exception


Re-upgrade an upgraded module
.............................

In some cases, you might want to try forcing the upgrade of a module which was already
upgraded by resetting the version of the module to a past version.

You might want to do that if you fix the migration script of a module after it was
migrated.

Example to update the known version of ``base`` to 14.0 so OpenUpgrade will try
to re-upgrade it to version 15:

``update ir_module_module set latest_version='14.0' where name='base';``

Learning resources
------------------

.. toctree::
   :maxdepth: 2

   migrationmanager
   devfaq

You can also refer to the following:

- `OpenUpgrade API <https://oca.github.io/OpenUpgrade/API.html>`_
- the code of OpenUpgrade API
  `openupgrade.py <https://github.com/OCA/openupgradelib/blob/master/openupgradelib/openupgrade.py>`_
