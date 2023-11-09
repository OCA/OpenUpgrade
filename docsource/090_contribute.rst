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
    `here <https://github.com/OCA/OpenUpgrade/issues/3681/>`_.
    
    Sometimes, the pull request is not yet registered in the issue, so it's not bad to do a search on the opened pull requests with the name of the module to look for.

  * Then, ensure that all the dependencies of the module are mark as ``done`` or
    ``Nothing to do`` in OpenUpgrade for that version.
    For that purpose, refer to :doc:`030_coverage_analysis`.
    In our example, check the ``depends`` key of the `manifest <https://github.com/odoo/odoo/blob/16.0/addons/account/__manifest__.py#L18>`_ of the ``account`` module 
    If some dependencies are missing, you should start by migrating these modules.

  * As other OCA contribution, create a new branch, from an up to date OCA branch:

    ``git checkout -b 16.0-mig-account``

  * Make a copy of the analysis file with the suffix ``_work``.

    ``cd ./openupgrade_scripts/scripts/account/16.0.1.2/``
    ``cp upgrade_analysis.txt upgrade_analysis_work.txt``

  * Explain the changes to do in the ``upgrade_analysis_work.txt``.
    Write ``pre-migration.py`` and / or ``post-migration.py`` scripts in the same folder.
    Comment / uncomment lines in ``noupdate_changes.xml``.
    (Read more in :doc:`080_migration_script_development`)

  * Finally, commit your changes.
    ``git add . && git commit -am "[OU-ADD] account"``
    (For a fix, use ``[OU-FIX]`` prefix)

  * Propose your changes to the community for review.
    ``git push MY_REMOTE 16.0-mig-account``

Community involvement
---------------------

Writing migration scripts for Odoo is a lot of work, that can not be
accomplished by a single party.  We need your help.

If you are at all interested in discussing strategic, functional or
technical issues, please post an issue on the Github project:
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

