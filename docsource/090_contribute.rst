Contribute
==========

In order to contribute to the OpenUpgrade project, please

* Post your code contributions as pull requests on
  https://github.com/OCA/OpenUpgrade
* Donate to the Odoo Community Association (https://github.com/sponsors/OCA)
* Hire any active contributor to this project to help you migrate your
  database, and give back any code improvements developed during the project.


How to contribute new migration scripts
---------------------------------------

To Contribute to OpenUpgrade you must make one pull request per module.

For example, if you want to propose the migration script of the ``account``
module from version 15.0 to version 16.0:

  * Always ensure that there is no work already in progress by a community member.
    For that purpose, go the issue named "Migration to version NN.0" on GitHub, where NN is the version for which you want to propose the script.
    `here <https://github.com/OCA/OpenUpgrade/issues?q=is%3Aopen++is%3Aissue+%22Migration+to+version%22+/>`_.
    
    Sometimes, the pull request is not yet registered in the issue, so it's not bad to do a search on the opened pull requests with the name of the module to look for.

  * Then, ensure that all the dependencies of the module are mark as ``done`` or
    ``Nothing to do`` in OpenUpgrade for that version.
    For that purpose, refer to :doc:`030_coverage_analysis`.
    In our example, check the ``depends`` key of the `manifest <https://github.com/odoo/odoo/blob/16.0/addons/account/__manifest__.py#L18>`_ of the ``account`` module 
    If some dependencies are missing, you should start by migrating these modules.

**Note**

It's not strictly necessary to make contributions in the order of dependency,
but you may face errors that are not related to your contribution, if you don't follow this order.
For example, the sale_stock migration script may fail, if the stock migration script has not been run upstream.

  * As other OCA contribution, create a new branch, from an up to date OCA branch:

  .. code-block:: shell

     git checkout -b 16.0-mig-account

  * Make a copy of the analysis file with the suffix ``_work``.

  .. code-block:: shell

     cd ./openupgrade_scripts/scripts/account/16.0.1.2/
     cp upgrade_analysis.txt upgrade_analysis_work.txt


  * Explain the changes to do in the ``upgrade_analysis_work.txt``.
    For each line, add a prefix, and explain your analysis:

    * ``NOTHING TO DO``, and why it's nothing to do
    * ``DONE``: pre-migration/post-migration: indicating the what and maybe the why.
    * ``TODO``: This shouldn't be usually done.

**Note:**
Place each marker **inline, on its own line, immediately following the
specific analysis line it annotates**. Don't consolidate multiple adjacent
analysis lines under a single grouped comment, even when the lines are
conceptually related — each gets its own one-line marker.

Empty section headers (e.g. ``---Models in module 'X'---`` with no
analysis lines below) get **no** marker — leave them blank. Only
sections with content are annotated; a whole module with nothing to do
is recorded in the coverage matrix (column 2), not by marking an empty
work-file section.

Markers are terse — typically ``# DONE: <one-line summary>`` or
``# NOTHING TO DO``. The "why" belongs in the commit message body or
PR description, not in the work file.

Example:

.. code-block:: text

    ---Fields in module 'X'---
    X / account.tax / l10n_in_is_lut (boolean): NEW
    # DONE: add_fields in pre-migration.
    X / account.tax / l10n_in_tax_type (selection): is now stored
    # DONE: add_fields in pre-migration; map_values for legacy selection set.
    X / res.partner / l10n_in_pan (char): DEL
    # NOTHING TO DO: new field name differs; update_db preserves old column as legacy.

    ---XML records in module 'X'---
    # NOTHING TO DO

  * Write ``pre-migration.py`` and / or ``post-migration.py`` scripts in the same folder.

  * Comment / uncomment lines in ``noupdate_changes.xml``.

(Read more in :doc:`080_migration_script_development`)

  * Finally, update the coverage file in ``docsource/modulesXX-YY.rst``, and mark the
    module as ``done``, ``Nothing to do``, etc.

(Read more in :doc:`coverage legend detail.<coverage_analysis/coverage_legend>`)

  * Finally, commit and push your changes.

  .. code-block:: shell

      git add .
      git commit -am "[MIG] account"
      git push MY_REMOTE 16.0-mig-account


  **Note:**

    * For a first-pass migration script for a module version, use ``[MIG]``.
      This is the dominant prefix on recent branches (e.g. ``[MIG] account``,
      ``[MIG] hr_recruitment``).

    * For a fix of an existing migration script, use ``[FIX]``.

    * For an improvement of an existing migration script, use ``[IMP]``.

    * For changes to the OpenUpgrade framework, infrastructure, or
      cross-cutting helpers (rather than a per-module migration script),
      use ``[OU-ADD]`` / ``[OU-FIX]`` / ``[OU-IMP]``. These prefixes
      originated in the V13-and-earlier era when OpenUpgrade shipped
      patched copies of Odoo source files, and they remain in use today
      for framework-level changes.

  * Propose your changes to the community for review, opening a Pull Request on github.

Community involvement
---------------------

Writing migration scripts for Odoo is a lot of work, that can not be
accomplished by a single party.  We need your help.

If you are at all interested in discussing strategic, functional or
technical issues, please post an issue on the GitHub project:
`<https://github.com/OCA/OpenUpgrade>`_.

If you are a developer, give the OpenUpgrade software a go and give us
feedback.  If you use the software, provide the project with your issue
reports and any migration scripts that you develop.  Help to improve the
developer tools and any existing or newly proposed migration script
contributed by others.

If you are an Odoo consulting company, use the tools to help your
customers migrate to a newer major release of Odoo and contribute
the scripts that you developed in the process.

If you are are using Odoo professionally within your organisation,
consider hiring a Odoo consulting company to migrate your configuration
using the technology provided by this project, and insist that the
resulting migration scripts be contributed back.

If you are an independent, knowledgeable user of Odoo and the OpenUpgrade
project covers the modules that you have in use, try and use the software
to upgrade a copy of your database and give us feedback.

Thank you!
