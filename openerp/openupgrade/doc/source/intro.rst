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
