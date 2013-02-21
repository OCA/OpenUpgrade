Status of the components
++++++++++++++++++++++++

The following components have been foreseen in the design of the OpenUpgrade
project:

     * An OpenERP module *OpenUpgrade Records* to generate and compare representations of installed modules on different versions of OpenUpgrade server. Status: stable.

     * A logging facility that dumps the OpenERP database layout in a format that can be processed further. It is included in the server distribution. This functionality has been implemented for OpenERP 5, 6.0 and 6.1. Status: deprecated by the OpenUpgrade Records module.

     * A number of scripts to process the database dump. The scripts are included in the server distribution. Status: deprecated by the OpenUpgrade Records module.

     * A libary with support functions to be called from the migration scripts. See :doc:`API`. This library is included in the server distribution. Status: stable.

     * A report facility that displays the user notes per module after an upgrade, and performs an analysis of required fields that were left empty on one or more records in the database, for the administrator to supply values for. Status: not yet developed.

     * Documentation for developers and users. You are currently reading it. The documentation is maintained in the latest server branch. Status: needs updating.

Module coverage
===============

For all official addons, migration scripts should be provided for migrating between subsequent major releases of OpenERP. This is the goal of the project. The design is such that the effort can be distributed between different developing parties. See below for an overview of module coverage per version.

.. toctree::
   :maxdepth: 2

   modules50-60
   modules60-61
   modules61-70


