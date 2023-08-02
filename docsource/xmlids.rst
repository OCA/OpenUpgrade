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

To manage changes to data defined with the noupdate flag,
please refer to the following use case :doc:`use_cases/xml_id_renaming`.
