Database analysis
+++++++++++++++++

Database analysis files are now included in the openupgrade-addons
distribution, so if you need to develop migration scripts for the
standard modules you do not need to run the analysis process yourself.
You can find the analysis file in the module's migrations directory
under the current version, in a file called openupgrade_analysis.txt

The analysis of the base module is included in the openupgrade-server
distribution. This module includes an additional file,
openupgrade_general_log.txt. This file contains some statistics as well
as the analysis records of modules that could not be found in the target
release of Odoo.

.. toctree::
   :maxdepth: 2

   analyse
   xmlids
   format
   strategies
