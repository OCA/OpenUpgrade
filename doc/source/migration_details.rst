Running the migration
=====================

Check out the code manually and upgrade your database by calling odoo-bin,
(or openerp-server) directly. You will want to do this when you are working on
developing migration scripts for uncovered modules.

1. Get the code from OpenUpgrade and dependencies
*************************************************

Make the `openupgrade_framework` and the `openupgrade_scripts` modules
available in the addons path in the Odoo instance of the new version.

Or, for older versions: check out the OpenUpgrade source code from Github
for the branches you need. Each branch migrates to its version from the
previous version, so branch 13.0 migrates from 12.0 to 13.0. If you are
migrating across multiple versions, you need to run each version of
OpenUpgrade in order. Skipping versions is not supported.

2. Check coverage of the migration scripts for your installed modules
*********************************************************************

Check if there are migration scripts provided for the set of modules that
are installed in your Odoo database. If there are modules for which no
migration scripts have been developed yet, your migration may fail or the
integrity of your database may me lacking. Check the module coverage in
this documentation.

At this stage, for some of the uncovered modules, you might want to uninstall
them from your database and re-install it later on after the migration.
This option might reduce the workload of the migration and can be applicable
for "ux" modules like ``web_widget_image_download`` if you did not
override this modules.


3. Make a copy the database to migrate
**************************************

Decide which database you are going to upgrade. You absolutely *must* make a
backup of your live database before you start this process!

4. Adjust your Odoo configuration
*********************************

Edit the configuration files and command line parameters to point to the
database you are going to upgrade. Run Odoo with the ``--update all
--stop-after-init --load=web,openupgrade_framework`` flags.

For versions earlier than 14.0 that are running the OpenUpgrade fork rather
than Odoo itself, you do not pass the `load` parameter.

5. Run and write and run and ... the Upgrade
********************************************

Run the upgrade and check for errors. You will probably learn a lot about
your data and have to do some manual clean up before and after the upgrade.
Expect to repeat the process several times as you encounter errors, clean up
your data, and try again. If necessary, ask for help or report bugs on
Github.

Add your migration scripts
--------------------------

There are plenty of examples in the code of existing migration scripts within
OpenUpgrade for your current version and from the previous versions.

You can also refer to the following documents:

- `The Odoo Migration Manager
  <https://doc.therp.nl/openupgrade/migrationmanager.html>`_
- `OpenUpgrade API <https://doc.therp.nl/openupgrade/API.html>`_
- the code of OpenUpgrade API
  `openupgrade.py <https://github.com/OCA/openupgradelib/blob/master/openupgradelib/openupgrade.py>`_
- `Development FAQ <https://doc.therp.nl/openupgrade/devfaq.html>`_

The Trial and error process for the development of your scripts
---------------------------------------------------------------

- [A] get the copy of your database in old version as `db-upgrade`, it is
  easy to do through the database manager of your old odoo
  `http://localhost:8012/web/database/manager`
- [B] run `odoo -d db-upgrade -u all --stop-after-init`
- [C] In case of error, fix the error (adding or editing migration
  scripts), then rerun **without** the `--upgrade all`:
  `odoo -d db-upgrade --stop-after-init`. This will continue the upgrade
  process from where it left off, starting with the module that caused the
  error. That way, the migration will not run the end-migration scripts of
  the modules that were already upgraded before the error, so in case of a
  live migration you always need to restore the database. But running this way
  will help you save a lot of time in the upgrade process.

Note that for the time being [C] is not available in all versions
(see explanations here: https://github.com/OCA/OpenUpgrade/pull/2499).
It is available for 12 and 13:
https://github.com/OCA/OpenUpgrade/pulls?q=is%3Apr+%5BFIX%5D+reset+exception

Whenever facing unexpected errors, you might want to restart from [A] as
the step [C] might leave your database in an inconsistent state.

Restart upgrade of the failed module instead of upgrading all systematically
----------------------------------------------------------------------------

*This can be seen as an alternative to the step [C] mentioned above.*

Try `--update=all` first and then when it fails on a given module
some_module, try to fix the scripts and do a ``--update=<some_module>``

This enables fixing and testing the some_module scripts

After it is fixed go back to ``--update=all`` because just doing
``--update=<some_module>`` and letting dependent modules is likely to lead
to partial and incomplete migration.

``fsync = off`` in your postgresql.conf
-------------------------------------

Use the Postgres configuration fsync=off for OpenUpgrade which gives a
significant boost (at the cost of zero security with the durability of
your data, that is never do that in production).

The config file can be found in ``/etc/postgresql/13/main/postgresql.conf``
in Linux and ``~/Library/Application\ Support/Postgres/var-*/postgresql.conf``
for iOS.

Read more about fsync config:
https://www.postgresql.org/docs/current/runtime-config-wal.html


General Tips
++++++++++++

* When installing the openupgradelib make sure you check out the latest version
  from github to get the latest updates and fixes::

    $ pip install git+git://github.com/OCA/openupgradelib.git

Configuration options (obsolete)
++++++++++++++++++++++++++++++++

Versions of OpenUpgrade earlier than 14.0 allow for the following configuration
options. Add these options to a separate stanza in the server configuration
file under a header *[openupgrade]*

* *autoinstall* - A dictionary with module name keys and lists of module names
  as values. If a key module is installed on your database, the modules from
  the value (and their dependencies) are selected for installation as well.

* *force_deps* - A dictionary with module name keys and lists of module names
  as values. If a key module is installed on your database, the modules from
  the value will be treated as a module dependency. With this directive, you
  can manipulate the order in which the modules are migrated. If the modules
  from the value are not already installed on your database, they will be
  selected for installation (as will their dependencies). Be careful not to
  introduce a circular dependency using this directive.
