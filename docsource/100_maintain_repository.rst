Maintain OpenUpgrade Repository
===============================

The following documentation is for OpenUpgrade Maintainers.

Set up the branch for a new Odoo release
----------------------------------------

Wait until the new branch was created via an entry in https://github.com/OCA/repo-maintainer-conf, then run the following script:

.. literalinclude:: maintainer_scripts/setup_new_branch.sh
  :language: shell

Finally, ``git push`` the branch on your fork, and make a pull request against OCA/$NEW branch.

Manual changes
--------------

* Execute the technical migration of ``upgrade_analysis`` from https://github.com/OCA/server-tools.

* Run the module migration, see https://github.com/OCA/OpenUpgrade/wiki/Crude-script-to-create-the-full-analysis-between-two-versions-of-Odoo. Run with Odoo configuration option module_coverage_file_folder = <some folder>.

* Add the coverage file from the step above (e.g. docsource/modules170-180.rst)

* On success, propose the migration of ``upgrade_analysis`` into server-tools

* PR adding a job for the new version in ``.github/workflows/generate-analysis-cron.yml`` on the current default branch of OpenUpgrade

* PR adding a job for the new version in ``.github/workflows/generate-testdb-cron.yml`` on the current default branch of OpenUpgrade

* Execute the technical migration of ``openupgrade_framework``.
