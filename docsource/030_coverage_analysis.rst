Coverage Analysis
=================

For all official addons, migration scripts should be provided for migrating
between subsequent major releases of Odoo. This is the goal of the project.
The design is such that the effort can be distributed between different
developing parties. See below for an overview of module coverage per version.

Check if there are migration scripts provided for the set of modules that
are installed in your Odoo database. If there are modules for which no
migration scripts have been developed yet, your migration may fail or the
integrity of your database may be lacking.
Refer to the :doc:`development` documentation to add the missing migration scripts.

.. toctree::
   :maxdepth: 1

   coverage_analysis/modules150-160
   coverage_analysis/modules140-150
   coverage_analysis/modules130-140
   coverage_analysis/modules120-130
   coverage_analysis/modules110-120
   coverage_analysis/modules100-110
   coverage_analysis/modules90-100
   coverage_analysis/modules80-90
   coverage_analysis/modules70-80
   coverage_analysis/modules61-70
   coverage_analysis/modules60-61
   coverage_analysis/modules50-60
