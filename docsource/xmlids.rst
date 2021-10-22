XML IDs
========
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

More interesting are data that are defined with the noupdate flag. In general,
you need to cover two cases in your scripts.

* Renamed XML ids of noupdate records. If a product category, or a res.groups
  entry has been renamed, you should pass them to
  :meth:`~openupgrade.rename_xmlids`
  so that the item in your current database survives the migration in its
  original form. If the XML id of a renamed noupdate record is not renamed
  this way, the new record will be created in addition to the existing one,
  and the existing record will lose its xml id.

* Modified fields of noupdate records, as collected in the
  `noupdate_changes.xml` in the migration analysis directory. When developing
  the migration scripts for a particular module, review this file and comment
  out any fields that must not be overwritten. If there is any data left that
  you want to take, load it from your post migration script using
  :meth:`~openupgrade.load_data`.
