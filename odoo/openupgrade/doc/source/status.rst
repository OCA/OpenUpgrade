Status of the components
++++++++++++++++++++++++

The following components have been foreseen in the design of the
OpenUpgrade project:

  * An Odoo module *OpenUpgrade Records* to generate and compare
    representations of installed modules on different versions of
    OpenUpgrade server.  Status: stable.

  * A number of scripts to process the database dump.  The scripts are
    included in the server distribution.  Status: deprecated by the
    OpenUpgrade Records module.

  * The *OpenUpgradelib* python library with support functions to be
    called from the migration scripts in this distribution or in the migration
    script of any community or private module to deal with migrations
    during the module lifecycle. See :doc:`API`. Status: stable.

  * A report facility that displays the user notes per module after an
    upgrade, and performs an analysis of required fields that were left
    empty on one or more records in the database, for the administrator
    to supply values for.  Status: not yet developed.

  * Documentation for developers and users.  You are currently reading
    it.  The documentation is maintained in the latest server branch.
    Status: needs updating.


Module coverage
===============

For all official addons, migration scripts should be provided for
migrating between subsequent major releases of Odoo.  This is the goal
of the project.  The design is such that the effort can be distributed
between different developing parties.
See below for an overview of module coverage per version for this release. For
earlier editions, see `<https://doc.therp.nl/openupgrade/status.html>`_

.. toctree::
   :maxdepth: 2

   modules120-130
   modules110-120
   modules100-110
   modules90-100
   modules80-90
   modules70-80
   modules61-70
   modules60-61
   modules50-60
