Maintain OpenUpgrade Repository
===============================

The following documentation is for OpenUpgrade Maintainers.

Set up the branch for a new Odoo release
----------------------------------------

.. literalinclude:: maintainer_scripts/setup_new_branch.sh
  :language: shell

Finally, ``git push`` the branch on your fork, and make a pull request against OCA/$NEW branch.

Manual changes
--------------

* Execute the technical migration of ``upgrade_analysis`` from https://github.com/OCA/server-tools.

* Run the module migration, see https://github.com/OCA/OpenUpgrade/wiki/Crude-script-to-create-the-full-analysis-between-two-versions-of-Odoo. Run with Odoo configuration option module_coverage_file_folder = <some folder>.

* On success, propose the migration of ``upgrade_analysis`` into server-tools, and the analysis files into ``openupgrade_scripts``.

* Add a coverage file (e.g. docsource/modules170-180.rst)

* In the ``OpenUpgrade``/``documentation`` branch, add a new line in ``build_openupgrade_docs``.

* Push a test database for the old release to Github (see https://github.com/OCA/OpenUpgrade/wiki/How-to-create-a-reference-database)

* Execute the technical migration of ``openupgrade_framework``.

* Check files in .github/workflows for any required changes.

* Once development starts on the new edition's migration scripts, change the default branch for new PRs at https://github.com/OCA/OpenUpgrade/settings/branches.
