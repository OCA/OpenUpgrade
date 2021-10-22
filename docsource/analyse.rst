How to run your own analysis
============================
If you do need to run your own analysis, you need to perform the following
steps.

* Set up two servers of subsequent Odoo releases. Make the following modules
  available: `upgrade_analysis` and `openupgrade_scripts`.

  In the case of a release before 14.0, you need to run the fork from the
  corresponding branch in https://github.com/oca/openupgrade. That fork also
  contains `openupgrade_records`.

* On both instances, install a database without demo data and
  install the *upgrade_analysis* module, which is included in the
  OpenUpgrade server distribution. This will add a menu
  *Upgrade Analysis* to the Settings menu.

* On both instances, install the modules that you need to write migration
  scripts for, or use the *Install Modules* from the *Upgrade Analysis* menu.

* On both instances: from the analysis menu, start the *Generate Records
  Wizard*.

* On the target instance (this is the more recent version): from the
  analysis menu, select the *Comparison Configuration* option and
  create a new config to connect to the other instance. In the form view of
  this configuration record , start a *New Analysis*.

The analysis files for each of the modules will be placed in the following
location:

* In the case of Odoo modules: in the path that is indicated by the
  `--upgrade-path` parameter of the Odoo server, or in the `scripts`
  folder of the `openupgrade_scripts` module directory if it is available in
  your addons path

* In the case of OCA or custom modules: in the `migrations/<version>`
  directory in the module directory itself.
