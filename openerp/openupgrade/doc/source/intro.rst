Introduction
============

OpenERP is an open source business application suite and development platform. Currently, the software does not support migrations from one major release to another. Instead, the migrations are part of a support package sold by OpenERP SA. This project aims to provide an Open Source upgrade path for OpenERP.

The project consists of several branches of two software projects on Launchpad:

* OpenUpgrade server: `<https://launchpad.net/openupgrade-server>`_

* OpenUpgrade addons: `<https://launchpad.net/openupgrade-addons>`_

These branches are copies of the OpenERP software, but are to be supplied with migration scripts for each module. The migration script updates that part of a database that is governed by the module for which it is written. We use the upgrade native mechanism in OpenERP, which was used in older versions of the OpenERP server and presumably still is for the proprietary upgrade path.

This way, perfect modularity is achieved. Any developer can contribute migration scripts for a single module. Of course, for every new major release of OpenERP, every substantial module needs a new migration script to cover the changes in that release. 

By design, the project aims at user-friendliness too. When all modules are provided migration scripts for, the user can simply install the OpenUpgrade software, run it on a copy of their OpenERP database with the *--update all* flag and restore the upgraded database onto the next major release of OpenERP. Of course, given the complexity of the software and the process this perfection is somewhat theoretical!

Apart from a collection of migration scripts, this project aims at providing developers with a set of tools that they can use to extract the changes that their migration scripts need to cover. You can read more on that in the :doc:`analysis` section.

Please do not use the OpenUpgrade software to run a live instance of your OpenERP database. It is not maintained for that purpose. Use the official OpenERP software for that.

Migrating Your Database
=======================

1. Check out the OpenUpgrade source code from Launchpad for the branches you
   need. Each branch migrates to its version from the previous version, so
   branch 6.0 migrates from 5.0 to 6.0. If you are skipping versions, you still
   need to run all the branches in between.

2. Compare your set of installed modules with the modules that are covered by
   the OpenUpgrade Addons branch you are using. Upgrading a database that has
   uncovered modules installed is likely to fail. Authoritative in this respect
   is the existence and contents of a *user_notes.txt* file in the
   migrations/[version] subdirectory of each module. We also try to indicate
   module coverage in the documentation but it sometimes lags behind.

3. Decide which database you are going to upgrade. You absolutely *must* make a
   backup of your live database before you start this process!

4. Edit the configuration files and command line parameters to point to the
   database you are going to upgrade. The parameters will probably be the same
   as you use on your live server, except they point to the OpenUpgrade
   addons source code, point to the database you want to upgrade, and add the
   *--update all --stop-after-init* flags.

5. Run the upgrade and check for errors. You will probably learn a lot about
   your data and have to do some manual clean up before and after the upgrade. 
   Expect to repeat the process several times as you encounter errors, clean up
   your data, and try again. If necessary, ask for help or report bugs on
   Launchpad.

6. Once the data migration is successful, run the official version of OpenERP
   against it to test how the migrated data behaves under the new version. 
   Remember that the OpenUpgrade version of the source code is only intended to 
   perform the migration, not run the OpenERP server.

Configuration options
=====================

OpenUpgrade allows for the following configuration options. Add these options
to a separate stanza in the server configuration file under a header 
*[openupgrade]*

* *autoinstall* - A dictionary with module name keys and lists of module names
  as values. If a key module is installed on your database, the modules from
  the value (and their dependencies) are selected for installation as well.

* *forced_deps* - A dictionary with module name keys and lists of module names
  as values. If a key module is installed on your database, the modules from
  the value will be treated as a module dependency. With this directive, you
  can manipulate the order in which the modules are migrated. If the modules
  from the value are not already installed on your database, they will be
  selected for installation (as will their dependencies). Be careful not to
  introduce a circular dependency using this directive.

