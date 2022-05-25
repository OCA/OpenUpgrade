This module is a technical module that contains a number of monkeypatches
to improve the behaviour of Odoo when migrating your database using the
OpenUpgrade migration scripts:

* Prevent dropping columns or tables in the database when fields or models
  are obsoleted in the Odoo data model of the target release. After the
  migration, you can review and delete unused database tables and columns
  using `database_cleanup`. See
  https://odoo-community.org/shop/product/database-cleanup-918
* When data records are deleted during the migration (such as views or other
  system records), this is done in a secure mode. If the deletion fails because
  of some unforeseen dependency, the deletion will be cancelled and a message
  is logged, after which the migration continues.
* Prevent a number of log messages that do not apply when using OpenUpgrade.
* Suppress log messages about failed view validation, which are to be expected
  during a migration.
* Run migration scripts for modules that are installed as new dependencies
  of upgraded modules (when there are such scripts for those particular
  modules)
