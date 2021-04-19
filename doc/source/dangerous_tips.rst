Dangerous Tips
++++++++++++++

Only for experts in need for desperate ideas to increase the development process.

Disclaimer / Warning
--------------------

If you see this page, it must be after multiple considerations whether it should or
should not be published within OpenUpgrade official documentation.

Why not publish it?

Because **the content of this page might lead you to big unrecoverable mess in your
data.**

Why still publish it?

Because you might be working on a very heavy migration, with a very large size database,
and if you know what you are doing, this page will help you saving time during the
development process of migration scripts.


Dangerous tip: uninstall modules which are not yet covered
----------------------------------------------------------

For some of the uncovered modules, you might want to uninstall
them from your database and re-install them later on after the migration.

This might reduce the workload of the migration and can be applicable
for "ux" modules, like ``web_widget_image_download``.

But, if you uninstall the wrong modules, **you might end up in losing data.**

To uninstall module, you can execute:

::

   UPDATE ir_module_module
   SET state = 'to remove'
   WHERE
       state IN ('to upgrade', 'to install')
       AND name in ('module_to_uninstall_1', 'module_to_uninstall_2')
   RETURNING name

Then run Odoo with ``-u dummy --stop-after-init`` to uninstall the modules
that could not be upgraded yet.

That way, you get a partially migrated database that you can login to and
perform UI testing.


Dangerous tip: ``fsync = off`` in your postgresql.conf
------------------------------------------------------

Use the Postgres configuration ``fsync=off`` for OpenUpgrade boost your migration
process (at the cost of zero security with the durability of
your data).

The config file can be found in ``/etc/postgresql/13/main/postgresql.conf``
in Linux and ``~/Library/Application\ Support/Postgres/var-*/postgresql.conf``
for OSx.

You should never do that in production, and this should not be used either while
you will be performing the actual database upgrade.

If you decide to use this, it should be only during the time to write the
migration scripts, and even that is discouraged as you might forget about
turning fsync back on and later one end up in unrecoverable data loss.

Read more about fsync config:
https://www.postgresql.org/docs/current/runtime-config-wal.html
