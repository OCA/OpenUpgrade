XML IDs
========
The OpenUpgrade analysis files give a representation of the XML IDs that a
module defines, in comparison with the previous release of the module.

Note, that if you run your own analysis on databases containing
demo data, you will get a lot of noise here. 

XML IDs which do not occur in the updated version of all installed modules
will be removed automatically by the OpenERP server, if they do not have
the noupdate attribute. 

You can ignore most entries here, most notably

    * ir.actions.*

    * ir.model.fields

    * ir.model

    * ir.ui.* [1]

    * res.country*

    * res.currency*

More interesting are

    * res.groups
      If a res groups has moved module (example: hr_manager moved from module
      hr to base in OpenERP 6), implement this change in the pre-upgrade script
      for the module from which it moved.

    * res.roles (migrating from OpenERP 5 to 6 only)
      These have been migrated to groups in OpenERP6. Find out which group has
      replaced this role and use the role migration function from openupgrade
      library module (TODO).

    * workflow.*
      These IDs indicate changes in the workflow schemes. You need to map any
      of such changes in nodes and transitions, and replace them in the
      wkf\_ tables.

    * Option lists, such as ...?
      You may need to map the fields on any resources refering to this option
      list value to one of the new value set for this option.

    * ir.model.access
      In general, if you apply group access in line with the original meaning,
      you should be able to ignore these. However, you will need to audit the
      model access for your setup anyway. These entries might be of a little
      help in that process.

    * Any general data added by the module. Typically, data is loaded one time
      only using the 'noupdate' flag in the XML. You cannot simply force-load
      such data in your upgrade script, or you will for instance reset the
      sequences used for invoice numbering. Revise any data carefully and
      copy relevant, new data in a separate file. Load it from your post script
      using :meth:`~openupgrade.load_xml` from the module :mod:`openupgrade`
      which is included with the OpenUpgrade Server package. You may also have
      to update specific attributes from existing resources.

[1] You might want to use this information to semi-automatically audit any manual
customizations. This subject falls out of scope of this project for now)
