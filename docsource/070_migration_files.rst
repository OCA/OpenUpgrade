Migration Files
===============

For each odoo module, a **migration directory** contains the analysis of
the differences between the previous version and the current version
and the migration scripts developed to ensure the migration
of this module runs properly.

For versions 14.0 and higher
----------------------------

Migration directories are hosted in `scripts` subdirectory of the
openupgrade_scripts module directory in the https://github.com/OCA/OpenUpgrade
repository.

For example, the migration folder for migrating the `account` module
from version 13.0 to version 14.0 is located here :

https://github.com/OCA/OpenUpgrade/tree/14.0/openupgrade_scripts/scripts/account/

For versions 13.0 and below
---------------------------

Migration directories are hosted in the `migration` folder of each module
in the forks of Odoo at https://github.com/OCA/OpenUpgrade.


For example, the migration folder for migrating the `account` module
from version 12.0 to version 13.0 is located here :

https://github.com/OCA/OpenUpgrade/tree/13.0/addons/account/migrations

Non official addons
-------------------

For OCA or custom addons, migration directories are hosted in the `migration`
folder of each module.

For example, the migration folder for migrating the OCA `account_global_discount` module
from version 12.0 to version 13.0 is located here :

https://github.com/OCA/account-invoicing/tree/13.0/account_global_discount

Directory contents
------------------

The contents of the migration directory per module are:

* A file `openupgrade_analysis.txt` that contains data model changes and
  changes in the set of XML records
* A file `openupgrade_analysis_work.txt` which is a copy of the previous file,
  annotated by the developers of the migration scripts
* A file `noupdate_changes.xml` containing changes that may need to be loaded
  during module migration (after reviewing the contents of this automatically
  generated file).
* A file `pre-migration.py` (or any Python file(s) starting with `pre-`) that
  is executed by the Odoo migration manager just before the module is loaded.
* A file `post-migration.py` (or any Python file(s) starting with `post-`) that
  is executed by the Odoo migration manager right after the module was loaded.
* A file `end-migration.py` (or any Python file(s) starting with `end-`) that
  is executed by the Odoo migration manager when all modules have been
  processed.

The migration directory of the base module contains an additional file
`openupgrade_general_log.txt`. This file contains some statistics as well
as the analysis records of modules that could not be found in the target
release of Odoo anymore.

Generate the difference analysis files
--------------------------------------

You can create a custom set of analysis files on any set of modules between
any two versions of Odoo using the `upgrade_analysis` module that is hosted
in https://github.com/oca/server-tools.
(for versions 13.0 or lower, the module is named `openupgrade_records` and is
place in each branch of the OpenUpgrade repository under
`odoo/addons/openupgrade_records` path)

Analysis files description
--------------------------

The first section displays models which are added or removed from the database.

The second section lists the model fields which have been signalled by the
analysis script. Every line lists the following columns:

module / model / field (field type) : description of the change

Multiple changes per field are listed on separate lines.
If possible, the old situation is added to the change description (in between
parentheses).

The change description flags the following types of change:

    * The field is now required. The upgrade script might apply the default for
      this field, if it is encoded in the model, or any value that you might see
      fit (see the openupgrade library
      function :meth:`~openupgrade.set_defaults`). If any empty values remain,
      these can be reported by the openupgrade report module (TODO).
      If the field is a function field after the upgrade, this changes the cause
      for action. See below.

    * A field is now a function or a related field. This might or might not call
      for any action of your upgrade script, as the value is now automatically
      determined. At the same time, this might cause data loss. An example is
      the field employee's manager (hr module), which in Odoo 6 is derived
      from the employee's department.

      Without any action in the upgrade script, you will lose the manually
      encoded employee hierarchy.

    * A selection field's hardcoded selection changes. You need to audit the
      function for any change in possible values and may need to map any
      differences you encounter.

    * A selection field's selection is now being filled by a function or has
      stopped doing so. You need to audit the function for any change in
      possible values and may need to map any differences you encounter.

      (Of course, a selection function could change the set of possible values
      in between functions.)

    * The field changes type. This always calls for action in your upgrade
      script. Rename the database column to a temporary name in the pre script,
      then migrate the values in the post script. A typical instance of this
      change is when the field becomes a many2one lookup table, or the other way
      around. An example of these are the partner's function which became a char
      field in Odoo 6, and the partner's title which as a selection (thus
      char type database column) and had to be migrated to a many2one on
      res.partner.title.

    * A relation field's relation changes. You need to migrate the one target
      model to the other, and update the references to them.

    * A field is deleted from the model (marked by 'DEL'). Also fields from
      deleted models are marked in this way. TODO: mark fields from deleted
      models in a distinct manner. Any distinct features of the field are
      displayed, for easier manual matching.
      You need to audit any new fields
      (see below) to see if they correspond to the deleted field and implement
      this change in your upgrade script. It might also be the case that a
      deleted field is now delegated to a new or existing _inherits table (see below).

    * A field is introduced in the model (marked by 'NEW'). Also fields from
      introduced models are marked in this way. TODO: mark fields from introduced
      models in a distinct manner? Any distinct features of the field are
      displayed, for easier manual matching. You need to audit any deleted
      fields (see below) to see if they correspond to the new field and
      implement this change in your upgrade script.

    * The _inherits property of a model has changed. It might be the case that
      fields which are removed are actually delegated to this newly
      inherited table.

    * A new model is introduced. Copy all access data from the access csv and
      security rules xml files and load them in your script. Also copy any
      other data that may be introduced in this release of Odoo. This may
      have consequences for other modules' migration scripts. TODO: create an
      overview of new or renamed modules.

The final section of the database layout analysis contains a simple report on
the changes that were detected.

XML IDs
-------

The OpenUpgrade analysis files give a representation of the XML IDs that a
module defines, in comparison with the previous release of the module.

XML IDs which do not occur in the updated version of all installed modules
will be removed automatically by the Odoo server, if they do not have
the noupdate attribute. Therefore, you can ignore most entries here, such as

    * ir.actions.*
    * ir.model.fields
    * ir.model.access
    * ir.model
    * ir.ui.*
    * res.country*
    * res.currency*

When XML ids of such record types change, the record will be recreated under
the new id, and the old record will be unlinked.

To manage changes to data defined with the noupdate flag,
please refer to the following use case :doc:`use_cases/xml_id_renaming`.