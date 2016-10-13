How to run your own analysis
============================
If you do need to run your own analysis, you need to perform the following
steps (the awkward processing of the server log file is now obsolete).

* Set up two OpenUpgrade servers of subsequent Odoo releases

* On both instances, install a database without demo data and
  install the *openupgrade_records* module, which is included in the
  OpenUpgrade server distribution. This will add a menu
  *OpenUpgrade Development* to the Administration menu.

* On both instances, install the modules that you need to write migration
  scripts for, or alternatively select *Install All Modules* from the
  Development menu.

* On both instances: from the development menu, select the *Generate Records*
  option.

* On the target instance (this is the more recent version): from the
  Development menu, select the *Comparison Config* option and
  create a new config to connect to the other instance. In the config's
  form, click on *Perform Analysis*.

Note that in many of the operations above you may get a client timeout or a
concurrent access error even if the operation completes successfully. You
should be able to assertain a succesful operation by verifying that all
modules involved are in an installed state and the analysis files in the
module directories have an appropriate modification time.
