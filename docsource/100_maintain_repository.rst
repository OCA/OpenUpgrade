Maintain OpenUpgrade Repository
===============================

The following documentation is for OpenUpgrade Maintainers.

Set up the branch for a new Odoo release
----------------------------------------

.. literalinclude:: maintainer_scripts/setup_new_branch.sh
  :language: shell

Finally, ``git push`` the branch on your fork, and make a pull request against OCA/$NEW branch.

Create a Reference Database
---------------------------

To run a test migration, the Github `Test` workflow downloads a preinstalled database of the previous version
from https://github.com/OCA/OpenUpgrade/releases/tag/databases.
This database has all Odoo core modules installed with demo data.

* Checkout a clean Odoo up-to-date base code
* Make sure your addons_path only contains odoo repo, (if it contains OCA / custom repo) the modules will be installed.
* Odoo version 11.0 may require this patch: https://github.com/odoo/odoo/pull/28620
* Generate the database

.. literalinclude:: maintainer_scripts/create_reference_database.sh
  :language: shell

* Upload the database ``.psql`` file present in the ``/tmp/`` folder [here](https://github.com/OCA/OpenUpgrade/releases/tag/databases).

To check if all is ok, you should migrate the ``openupgrade_scripts`` module (first) and then the ``openupgrade_framework`` module, and check if the CI is OK.

Manual changes
--------------

* Execute the technical migration of ``upgrade_analysis`` from https://github.com/OCA/server-tools.

* Run the module migration, see https://github.com/OCA/OpenUpgrade/wiki/Crude-script-to-create-the-full-analysis-between-two-versions-of-Odoo. Run with Odoo configuration option module_coverage_file_folder = <some folder>.

* On success, propose the migration of ``upgrade_analysis`` into server-tools, and the analysis files into ``openupgrade_scripts``.

* Add a coverage file (e.g. docsource/modules170-180.rst)

* In the ``OpenUpgrade``/``documentation`` branch, add a new line in ``build_openupgrade_docs``.

* Execute the technical migration of ``openupgrade_framework``.

* Check files in .github/workflows for any required changes.

* Once development starts on the new edition's migration scripts, change the default branch for new PRs at https://github.com/OCA/OpenUpgrade/settings/branches.
