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


The branches in the first project contain the framework, as well as the
database analysis and the migration scripts.

The second project contains a library with helper functions. It
can be used in the migration of any Odoo module.

Older versions
--------------
Before Odoo 14.0, the branches in https://github.com/OCA/openupgrade
contain copies (or forks in Git terminology) of the Odoo main project, but
with extra commits that include the framework, and the analysis and the
migration scripts for each module.

Contribute
----------
In order to contribute to the OpenUpgrade project, please

* Post your code contributions as pull requests on
  https://github.com/oca/openupgrade
* Donate to the Odoo Community Association (https://github.com/sponsors/OCA)
* Hire any active contributor to this project to help you migrate your
  database, and give back any code improvements developed during the project.

Migrating your database
=======================

.. toctree::
   :maxdepth: 2

   migration_details
   after_migration
