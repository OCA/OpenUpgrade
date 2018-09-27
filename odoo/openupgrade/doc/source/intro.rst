Introduction
============

Odoo is an open source business application suite and development platform.
This project, *OpenUpgrade*, aims to provide an Open Source upgrade path for
Odoo. This is a community initiative, as the open source version of Odoo
does not support migrations from one major release to another. Instead,
migrations are part of a support package sold by Odoo SA. Note that the name
of the project refers to the old name of Odoo, *OpenERP*.

The project is hosted as two separate GitHub projects:

* https://github.com/OCA/openupgrade
* https://github.com/OCA/openupgradelib

The branches in the first project are copies (forks in Git terminology) of the
Odoo main project, but with extra commits that include migration scripts for
each module. The second project contains a library with helper functions. It
can be used in the migration of any Odoo module.

One
migration script updates that part of a database that is governed by the module
for which it is written.  We use the native upgrade mechanism in Odoo, which
was used in older versions of the Odoo server and presumably is still
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
