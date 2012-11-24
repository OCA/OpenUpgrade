Status of the components
========================

The following components have been foreseen in the design of the OpenUpgrade
project:

     * A logging facility that dumps the OpenERP database layout in a format that can be processed further. It is included in the server distribution. This functionality has been implemented for OpenERP 5, 6.0 and 6.1. Status: usable.

     * A number of scripts to process the database dump. The scripts are included in the server distribution. Status: usable.

     * A libary with support functions to be called from the migration scripts. See :doc:`API`. This library is included in the server distribution. Status: the library provides all functions that are currently called for in the migration scripts.

     * A report facility that displays the user notes per module after an upgrade, and performs an analysis of required fields that were left empty on one or more records in the database, for the administrator to supply values for. Status: not yet developed.

     * For all official addons, migration scripts should be provided for migrating between major releases of OpenERP. This is the goal of the project. For OpenERP 5 -> 6.0, there are migration scripts for the *base* and *account* modules (incl. analytic), but not the dependencies *process*, *board* and *product*. For OpenERP 6.0 -> 6.1, see :doc:`modules60-61`.
     
     * Documentation for developers and users. You are currently reading it. The documentation is maintained in the latest server branch. Status: always to be improved upon!

.. toctree::
   :maxdepth: 2

   modules60-61


