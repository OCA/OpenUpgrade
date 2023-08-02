The Odoo Migration Manager
==========================

The core mechanism that OpenUpgrade relies on is the migration manager that is
already built into Odoo itself. It is this mechanism that was used by Odoo to
run migrations back in the days before TinyERP 4.2 when migration scripts where
still included in the code. The same mechanism is probably still used by Odoo
internally to run the proprietary migration, and occasionally it is used in
the code to fix glitches during the Odoo release lifecycle. For an example,
see  `<https://github.com/odoo/odoo/commit/8b02879ff5>`_.

Please have a look at the docstring of the Odoo migration manager:
`<https://github.com/odoo/odoo/blob/7c95c14c06d77e5ebbd7aafd9c0c345b47d27d30/odoo/modules/migration.py#L23>`_. You will see that migration scripts are organized in the *migrations*
subdirectory in the module itself, in subdirectories per module version. The
scripts will be executed when the module is upgraded, if the installed version
of the module is lower than the name of the versioned directories.

There are three migration stages at which you can have migration scripts
executed: *before* the module is loaded (pre stage), *after* the module is
loaded into the database (post stage) and when *all* the modules are loaded
(end stage). The end stage was introduced into Odoo 9.0. In earlier versions
of OpenUpgrade, a file *odoo/openupgrade/deferred_<VERSION>.py* was
maintained to collect migration steps to be run after a full upgrade.

Note that you can use this mechanism for your own custom
module's lifecycle outside of the OpenUpgrade context. For that reason, the
OpenUpgrade helper methods were collected into the python openupgradelib that
you can make available in any Odoo instance using the *pip* tool.

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

FAQ
---

How are new dependencies treated by the Odoo migration manager?
   New dependencies (like the *edi* module is a new dependency of the
   *account* module) will be detected by the upgrade process.  The
   Odoo server code is slightly modified to loop over this part
   of the process to install new dependencies and then return to
   upgrading the modules that depend on them, until no more modules
   are processed.

Are migration scripts fired when installing new modules?
   Yes.  That includes any new dependencies that the new version of any
   module might declare.  You might want to check for a non true value
   of the *version* argument, or (better) make your script robust to
   running against a database that it does not apply to, in anticipation
   of any unknown unknowns.  Also another argument for not running the
   OpenUpgrade server in production, even though we both know that you
   would never ever do so anyway. Developers are free to corrupt the regular
   workings of Odoo if it helps the migration. For instance, from OpenUpgrade
   9.0 on, the workflow engine is disabled during field recomputation.
