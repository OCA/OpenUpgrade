Running the migration
=====================

Check out the code manually and upgrade your database by calling odoo-bin,
(or openerp-server) directly. You will want to do this when you are working on
developing migration scripts for uncovered modules.

1. Get the code from OpenUpgrade and dependencies
*************************************************

OpenUpgrade
...........

Make the `openupgrade_framework` and the `openupgrade_scripts` modules
available in the addons path in the Odoo instance of the new version.

Or, for older versions: check out the OpenUpgrade source code from Github
for the branches you need. Each branch migrates to its version from the
previous version, so branch 13.0 migrates from 12.0 to 13.0. If you are
migrating across multiple versions, you need to run each version of
OpenUpgrade in order. Skipping versions is not supported.

The OpenUpgrade repository includes both `openupgrade_framework` and
`openupgrade_scripts`:

https://github.com/OCA/openupgrade

openupgradelib
..............

* When installing the openupgradelib make sure you check out the latest version
  from github to get the latest updates and fixes::

    pip install git+https://github.com/OCA/openupgradelib.git@master#egg=openupgradelib

2. Check coverage of the migration scripts for your installed modules
*********************************************************************

Check if there are migration scripts provided for the set of modules that
are installed in your Odoo database. If there are modules for which no
migration scripts have been developed yet, your migration may fail or the
integrity of your database may be lacking. Check the module coverage in
this documentation under :doc:`status` and refer to the :doc:`development`
documentation to add the missing migration scripts.

3. Make a copy of the database to migrate
*****************************************

Decide which database you are going to upgrade. You absolutely *must* make a
backup of your live database before you start this process!

4. Adjust the configuration for Odoo and OpenUpgrade
****************************************************

Edit the configuration files and command line parameters to point to the
database you are going to upgrade. The recommended command line parameters are the
``--update all --stop-after-init --load=base,web,openupgrade_framework`` flags.

For versions earlier than 14.0 that are running the OpenUpgrade fork rather
than Odoo itself, you do not pass the `load` parameter.

Configuration options
.....................

* When migrating across several versions of Odoo, setting the target version
  as an environment variable allows OpenUpgrade to skip methods that are called
  in every version but really only need to run in the target version. Make the
  target version available to OpenUpgrade with::

    export OPENUPGRADE_TARGET_VERSION=13.0

  (when migrating up to 13.0)

Obsolete options in the Odoo configuration file
...............................................

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

5. Run the upgrade, fix data and repeat...
******************************************

Run the upgrade and check for errors. You will probably learn a lot about
your data and have to do some manual clean up before and after the upgrade.
Expect to repeat the process several times as you encounter errors, clean up
your data, and try again. If necessary, ask for help or report bugs on
Github.

Write the missing migration scripts
...................................

At this stage, if some of your modules don't have yet migration scripts,
you might need to add them yourself.
Read more about the development of migrations scripts in :doc:`development`
