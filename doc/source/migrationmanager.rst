The Odoo Migration Manager
++++++++++++++++++++++++++

The core mechanism that OpenUpgrade relies on is the migration manager that is
already built into Odoo itself. It is this mechanism that was used by Odoo to
run migrations back in the days before TinyERP 4.2 when migration scripts where
still included in the code. The same mechanism is probably still used by Odoo
internally to run the proprietary migration, and occassionally it is used in
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
OpenUpgrade helper methods were collected into the python Openupgradelib that
you can make available in any Odoo instance using the *pip* tool.
