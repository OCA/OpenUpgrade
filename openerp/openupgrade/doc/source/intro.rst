Introduction
============

Odoo is an open source business application suite and development platform.
Currently, the software does not support migrations from one major release to
another.  Instead, the migrations are part of a support package sold by
Odoo SA.  This project aims to provide an Open Source upgrade path for
Odoo.

The project is hosted as GitHub branches:
https://github.com/OpenUpgrade/OpenUpgrade

These branches are copies (forks in Git terminology) of the Odoo main project,
but with extra commits that include migration scripts for each module.  One
migration script updates that part of a database that is governed by the module
for which it is written.  We use the upgrade native mechanism in Odoo, which
was used in older versions of the Odoo/Odoo server and presumably is still
there for the proprietary upgrade path.

This way, perfect modularity is achieved.  Any developer can contribute
migration scripts for a single module.  Of course, for every new major release
of Odoo, every substantial module needs a new migration script to cover the
changes in that release.

By design, the project aims at user-friendliness too.  When all modules are
provided migration scripts for, the user can simply install the OpenUpgrade
software, run it on a copy of their Odoo database with the *--update all*
flag and restore the upgraded database onto the next major release of Odoo.
Of course, given the complexity of the software and the process this perfection
is somewhat theoretical!

Apart from a collection of migration scripts, this project aims at providing
developers with a set of tools that they can use to extract the changes that
their migration scripts need to cover. You can read more on that in the
:doc:`analysis` section.

Please do not use the OpenUpgrade software to run a live instance of your
Odoo database.  It is not maintained for that purpose.  Use the official
Odoo software for that.


Migrating your database
=======================

.. toctree::
   :maxdepth: 2

   migrate.py
   migration_details
   after_migration