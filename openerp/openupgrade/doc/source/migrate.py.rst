Automated migration script
==========================

Introduction
------------

For users who just want to run a migration, there is the convenience script migrate.py that takes care of downloading the necessary branches, set up a configuration for the migration and passing the correct parameters to the OpenUpgrade server.

Download it from launchpad_.

It accepts a couple of parameters, the mandatory ones are

``--config=[your original config file]``
  this file will be used to craft a new config file for the migration process

``--database=[the database to migrate]``
  this database will be migrated. The script takes care of making a copy of it before running the migration, your migrated database will be called ${name}_migrated.

``--run-migrations=[list of migrations to run]``
  the migrations to run. Note: You always name the target migration, so if you want to migrate a 6.1 database to 7.0, you pass ``--run-migrations=7.0``. For multiple migrations, i.e. migrate a 6.0 database to 7.0, separate the versions with a comma: ``--run-migrations=6.1,7.0``

(use ``--help`` for some other handy ones)

Have a cup of tea now, it will take a while. When it's done, the first thing you should do is to examine ``/var/tmp/openupgrade/migration.log``. Carefully read through eventual warnings, there will be a lot, most of them not fatal. If nothing weird showed up there, enjoy using your new database with the target version of OpenERP.

Problems
--------

Please report problems to https://answers.launchpad.net/openupgrade-server (very often, it's not a bug but a specific issue with your database setup). Make sure to have read your ``migration.log`` file carefully to avoid posting about obvious issues. Post relevant lines from the logfile, but don't post the whole logfile. If you can't decide what would be relevant, upload the file somewhere and link to that in your question.

In a nutshell
-------------

::

  bzr cat lp:openupgrade-server/scripts/migrate.py > migrate.py
  python migrate.py --config=[your openerp.conf] --database=[your database] --run-migrations=[your migrations]

.. _launchpad: http://bazaar.launchpad.net/~openupgrade-committers/openupgrade-server/7.0/view/head:/scripts/migrate.py
