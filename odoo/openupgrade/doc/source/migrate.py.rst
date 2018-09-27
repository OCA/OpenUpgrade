Automated migration script
==========================

Introduction
------------

**note that the original maintainer of this script deprecated this in favor
of a dedicated buildout as described in
https://github.com/OCA/OpenUpgrade/issues/502, at the moment, this script
won't be able to migrate to versions above 9.0**

For users who just want to run a migration, there is the convenience script
migrate.py that takes care of downloading the necessary branches, set up a
configuration for the migration and passing the correct parameters to the
OpenUpgrade server.

Download it from github_.

The script assumes that all python libraries that are required by Odoo are
installed in the current environment.

The script accepts a couple of parameters, the mandatory ones are

``--config=[your original config file]``
  this file will be used to craft a new config file for the migration process

``--database=[the database to migrate]``
  this database will be migrated.  The script takes care of making a copy of
  it before running the migration, your migrated database will be called
  ${name}_migrated.

``--run-migrations=[list of migrations to run]``
  the migrations to run.  Note: You always name the target migration, so if
  you want to migrate a 6.1 database to 7.0, you pass ``--run-migrations=7.0``.
  For multiple migrations, i.e. migrate a 6.0 database to 7.0, separate the
  versions with a comma: ``--run-migrations=6.1,7.0``

(use ``--help`` for some other handy ones)

Have a cup of tea now, it will take a while.  When it's done, the first thing
you should do is to examine ``/var/tmp/openupgrade/migration.log``.
Carefully read through eventual warnings, there will be a lot, most of them not
fatal.  If nothing weird showed up there, enjoy using your new database with
the target version of Odoo.


Problems
--------

Please report problems to https://github.com/OCA/openupgrade/issues
(very often, it's not a bug but a specific issue with your database setup).
Make sure to have read your ``migration.log`` file carefully to avoid posting
about obvious issues.  Post relevant lines from the logfile, but don't post
the whole logfile.  If you can't decide what would be relevant, upload the
file somewhere and link to that in your question.


In a nutshell
-------------

::

  wget https://raw.githubusercontent.com/OCA/OpenUpgrade/HEAD/scripts/migrate.py
  python migrate.py --config=[your odoo.conf] --database=[your database] --run-migrations=[your migrations]

.. _github: https://github.com/OCA/OpenUpgrade/blob/11.0/scripts/migrate.py
