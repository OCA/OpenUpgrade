PyCharm step by step guide
==========================

This guide explains how to perform an upgrade with PyCharm as an IDE, it is a variant of migration_details

General Schema
++++++++++++++

OpenUpgrade is an open tool that allows migrating an Odoo database from one version to another. All migrations have to be carried out between sequential versions, e.g. from 9 to 10 or from 10 to 11; it is not possible to skip a version.

OpenUpgrade is available at https://github.com/OCA/OpenUpgrade and consists of a complete Odoo version.

The flow is as follows (for example migrating from version 10 to 11):

1. Prepare the database from the current Odoo 10 project.
2. Create an instance of OpenUpgrade branch 11.
3. Launch pre-migration scripts on that database.
4. Launch the OpenUpgrade 11 installation updating the database on all the modules.
5. Launch post-migration scripts on that database.
6. Start the Odoo 11 installation and open the migrated database.


Prepare your development environment
++++++++++++++++++++++++++++++++++++

This instructions should cover most environments in use. Of course you can try it in other environments, but the aim of this document is to have a simple way to do the upgrade, not to cover all options.

Prerequisites: Ubuntu, Pycharm, PostgreSQL, Python 2, Python 3 (if upgrading to 11) and Odoo

Note: to make document simpler we use example names you need to adapt to your system. If you do so, don’t forget to change them in all of the following steps.

1. Create a postgresql user, in order to make visible the original database in all the migration process.

2. openupgradelib installation

   Clone https://github.com/OCA/openupgradelib to /openupgradelib folder (don’t install from pip or other repositories, they are not updated)

   Run setup.py from python 2 and again from python 3 (if you plan to migrate to Odoo 11)

   If you are migrating to Odoo 11 and python 3 does not recognise openupgradelib, you can install openupgradelib on this way:

   .. code-block:: bash

     $ pip3 install git+https://github.com/OCA/openupgradelib.git@master --upgrade

3. Create a PyCharm project in /old_version folder and call it “old_version”

   Clone the desired version of the Odoo repository to /old_version folder and also add your additional modules

   Create a PyCharm configuration to run Odoo as usual and call it “conf_old_version”.

   Script path: */old_version/odoo/odoo-bin*
   (exchange “odoo-bin” with “openerp-server” for versions prior to 10)

   Parameters:

   .. code-block:: console

     --db_name=odoo_db
     --db_user=database_user_name
     --db_password=database_user_pwd
     --db_host=localhost
     --db_port=5432
     --data-dir=/opt/data_dir
     --addons-path=/old_version/odoo/odoo/addons,/old_version/odoo/addons

   .. image:: images/pycharm_config.png

4. Create a PyCharm project in /new_version folder and call it “new_version_upgrade”.

   Clone your target version of OpenUpgrade repository to /new_version/OpenUpgrade.

   Clone server-tools_ repository to /new_version/OCA/server-tools

   1. Create a Pycharm configuration to run pre-migration and call it “conf_new_version_pre”:

      Script path: /new_version/OpenUpgrade/odoo/openupgrade/doc/source/scripts/pre-migration.py

      Parameters:

      .. code-block:: console

        --db_host=localhost
        --db_name=odoo_db_migrated
        --db_password=database_user_password
        --db_port=5432
        --db_user=odoo

      This step is intended to run any code you need, previous to run migration. In our case, we will prepare database to install the database_cleanup module for cleaning up after the migration.

   2. Create a PyCharm configuration to run migration and call it “conf_new_version_migration”:

      Script path: */new_version/OpenUpgrade/odoo-bin*

      Parameters:

      .. code-block:: console

        --addons-path=/new_version/OpenUpgrade/addons,/new_version/OpenUpgrade/odoo/addons,/new_version/OCA/server-tools
        --data-dir=/opt/data_dir
        --db_host=localhost
        --db_name=odoo_db_migrated
        --db_password=database_user_password
        --db_port=5432
        --db_user=odoo
        --load=web
        --stop-after-init
        --update=all

   3. Create a Pycharm configuration to run post-migration and call it “conf_new_version_post”.

      Script path: */new_version/OpenUpgrade/odoo/openupgrade/doc/source/scripts/post-migration.py*

      Parameters:

      .. code-block:: console

        --db_host=localhost
        --db_name=odoo_db_migrated
        --db_password=database_user_password
        --db_port=5432
        --db_user=odoo

5. Create a PyCharm project in /new_version folder and call it “new_version”.

   Clone your target version of Odoo repository to /new_version/odoo folder

   Create a Pycharm configuration to run odoo as usual and call it “conf_new_version”.

   Script path: */new_version/odoo/odoo-bin*

   Parameters:

   .. code-block:: console

     --addons-path=/new_version/odoo/addons,/new_version/odoo/odoo/addons,/new_version/OCA/server-tools
     --data-dir=/opt/data_dir
     --db_host=localhost
     --db_name=odoo_db_migrated
     --db_password=database_user_password
     --db_port=5432
     --db_user=odoo
     --load=web

For the Pycharm run configurations you can also copy the configurations_ to your .idea/runConfiurations directory in your project and adapt them to your config


Prepare your database
+++++++++++++++++++++

1. Open your “old_version” PyCharm project and run the “conf_old_version” PyCharm configuration.
2. Open the url to the instance in your browser, go to web/database/manager and duplicate your original database “odoo_db” to “odoo_db_migrated”.
3. Stop the PyCharm configuration once duplication of the database is finished.


Run the upgrade
+++++++++++++++

1. Open “new_version_upgrade” PyCharm project.

   *Optionally* run “conf_new_version_pre” pycharm configuration. This runs pre-migrate script. You can customize this script to fit your needs.

   If it doesn’t print any traces or errors and exit code is 0 continue with next step.

2. Run “conf_new_version_migration” PyCharm configuration.

   This runs the OpenUpgrade.

   If it doesn’t print any traces or errors and exit code is 0 continue with next step.

3. Run “conf_new_version_post” PyCharm configuration.

   This runs post-migrate script to clean your database.

   If it doesn’t print any traces or errors and exit code is 0 continue with testing the migrated instance.

Test results
++++++++++++

1. Open “new_version” Pycharm project and run it with “conf_new_version” pycharm configuration.

   Open the url to the instance in your browser, go to web/database/selector and login to your database “odoo_db_migrated”.
   Enjoy testing your database information ;-)

2. *Optionally*, run Odoo automated tests.

   This does a deep test of your database and can discover issues we will not be able to see with manual testing.

   To do so just create a Pycharm configuration based on “conf_new_version_post” and run it with following parameters:

   .. code-block:: console

     --addons-path=/new_version/odoo/addons,/new_version/odoo/odoo/addons,/new_version/OCA/server-tools
     --data-dir=/opt/data_dir
     --db_host=localhost
     --db_name=database_name
     --db_password=database_user_password
     --db_port=5432
     --db_user=odoo
     --load=web
     --log-level=test
     --test-enable
     --update=all
     --stop-after-init

   Be careful, automated t--db_name=database_to_migrate --db_user=odoo --db_password=1234 --db_host=localhost --db_port=5432ests have the following requirements:

   * admin user has to have the default password
   * english language needs to be installed and activated for the admin user

   Tip: if you want to test just one module change following parameter::

     --update=module__name


.. _server-tools: https://github.com/OCA/server-tools
.. _configurations: https://github.com/OCA/OpenUpgrade/odoo/openupgrade/doc/source/pycharm_configs