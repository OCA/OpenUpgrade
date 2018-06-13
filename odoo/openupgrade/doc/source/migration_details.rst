Manual migration
================

Instead of running *migrate.py*, you can also check out the code manually
and upgrade your database by calling odoo-bin (or openerp-server) directly. You
will want to do this when you are working on developing migration scripts for
uncovered modules.

General Tips
++++++++++++

* If you migrate your database through multiple versions make sure you use separate directories. If you use one directory and just check out a new branch the remaining *.pyc* files will cause trouble.

* When installing the openupgradelib make sure you check out the latest version from github to get the latest updates and fixes. Either by following the method from *migrate.py* or installing via pip like this::

    $ pip install --upgrade git+git://github.com/OCA/openupgradelib.git

Steps for manual migration
++++++++++++++++++++++++++

1. Check out the OpenUpgrade source code from Github for the branches you
   need. Each branch migrates to its version from the previous version, so
   branch 7.0 migrates from 6.1 to 7.0. If you are skipping versions, you still
   need to run all the branches in between.

   .. code-block:: bash

       $ git clone https://github.com/OCA/OpenUpgrade.git
       $ cd OpenUpgrade
       $ git checkout 11.0
       $ pip install -r requirements.txt
       $ pip install --upgrade git+git://github.com/OCA/openupgradelib.git
       $ cd ..

2. Compare your set of installed modules with the modules that are covered by
   the OpenUpgrade Addons branch you are using. Upgrading a database that has
   uncovered modules installed is likely to fail. Authoritative in this respect
   is the existence and contents of a *user_notes.txt* file in the
   migrations/[version] subdirectory of each module. We also try to indicate
   module coverage in the documentation but it sometimes lags behind.

   .. code-block:: bash

       $ diff odoo/addons OpenUpgrade/addons/ | grep -v "Common subdirectories" | grep -v "OpenUpgrade"
       Only in odoo/addons: account_accountant
       Only in odoo/addons: account_analytic_analysis
       Only in odoo/addons: account_analytic_plans
       Only in odoo/addons: account_cash_basis_base_account
       ...


3. Decide which database you are going to upgrade. You absolutely *must* make a
   backup of your live database before you start this process!
   On a development system you can do this by using the database manager (should be available in http://localhost:8069/web/database/manager)

   .. image:: images/DatabaseManager.png

4. Edit the configuration files and command line parameters to point to the
   database you are going to upgrade. The parameters will probably be the same
   as you use on your live server, except they point to the OpenUpgrade
   addons source code, point to the database you want to upgrade, and add the
   *--update all --stop-after-init* flags.

   .. code-block:: bash

       $ OpenUpgrade/odoo-bin --addons-path OpenUpgrade/addons --database odoo_10_migrate_to_v11 --update all --stop-after-init

5. Run the upgrade and check for errors. You will probably learn a lot about
   your data and have to do some manual clean up before and after the upgrade.
   Expect to repeat the process several times as you encounter errors, clean up
   your data, and try again. If necessary, ask for help or report bugs on
   Github.

6. Once the data migration is successful, run the official version of Odoo
   against it to test how the migrated data behaves under the new version.
   Remember that the OpenUpgrade version of the source code is only intended to
   perform the migration, not run the Odoo server.

Configuration options
+++++++++++++++++++++

OpenUpgrade allows for the following configuration options. Add these options
to a separate line in the server configuration file under a header
*[openupgrade]*

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

Errors and Solutions
++++++++++++++++++++

openupgradelib not from git
---------------------------

  When the upgrade fails with a database initialization error like "AttributeError: 'str' object has no attribute 'decode'"

  .. code-block:: console

    2018-06-13 07:55:44,526 10563 CRITICAL odoo_10_migrate_to_v11 odoo.service.server: Failed to initialize database `odoo_10_migrate_to_v11`.
    Traceback (most recent call last):
      File "/home/user/.virtualenvs/python3/lib/python3.6/site-packages/openupgradelib/openupgrade.py", line 1200, in wrapped_function
        if use_env2 else cr, version)
      File "/home/user/OpenUpgrade/odoo/addons/base/migrations/11.0.1.3/pre-migration.py", line 87, in migrate
        fill_cron_action_server_pre(env)
      File "/home/user/OpenUpgrade/odoo/addons/base/migrations/11.0.1.3/pre-migration.py", line 32, in fill_cron_action_server_pre
        openupgrade.add_fields(
    AttributeError: module 'openupgradelib.openupgrade' has no attribute 'add_fields'

    During handling of the above exception, another exception occurred:

    Traceback (most recent call last):
      File "/home/user/OpenUpgrade/odoo/service/server.py", line 925, in preload_registries
        registry = Registry.new(dbname, update_module=update_module)
      File "/home/user/OpenUpgrade/odoo/modules/registry.py", line 85, in new
        odoo.modules.load_modules(registry._db, force_demo, status, update_module)
      File "/home/user/OpenUpgrade/odoo/modules/loading.py", line 350, in load_modules
        loaded_modules, processed_modules = load_module_graph(cr, graph, status, perform_checks=update_module, report=report, upg_registry=upg_registry)
      File "/home/user/OpenUpgrade/odoo/modules/loading.py", line 139, in load_module_graph
        migrations.migrate_module(package, 'pre')
      File "/home/user/OpenUpgrade/odoo/modules/migration.py", line 174, in migrate_module
        migrate(self.cr, installed_version)
      File "/home/user/.virtualenvs/python3/lib/python3.6/site-packages/openupgradelib/openupgrade.py", line 1204, in wrapped_function
        (module, filename, str(e).decode('utf8')))
    AttributeError: 'str' object has no attribute 'decode'

  You need to make sure to use the openupgradelib from github:

  .. code-block:: bash

    $ pip install --upgrade git+git://github.com/OCA/openupgradelib.git


OpenUpgrade to version 11 called with python2
---------------------------------------------

  When the upgrade fails with a database initialization error like "load_module arg#2 should be a file or None"

  .. code-block:: console

    2018-06-13 07:47:18,143 6739 CRITICAL odoo_10_migrate_to_v11 odoo.service.server: Failed to initialize database `odoo_10_migrate_to_v11`.
    Traceback (most recent call last):
      File "/home/user/OpenUpgrade/odoo/service/server.py", line 925, in preload_registries
        registry = Registry.new(dbname, update_module=update_module)
      File "/home/user/OpenUpgrade/odoo/modules/registry.py", line 85, in new
        odoo.modules.load_modules(registry._db, force_demo, status, update_module)
      File "/home/user/OpenUpgrade/odoo/modules/loading.py", line 350, in load_modules
        loaded_modules, processed_modules = load_module_graph(cr, graph, status, perform_checks=update_module, report=report, upg_registry=upg_registry)
      File "/home/user/OpenUpgrade/odoo/modules/loading.py", line 139, in load_module_graph
        migrations.migrate_module(package, 'pre')
      File "/home/user/OpenUpgrade/odoo/modules/migration.py", line 165, in migrate_module
        mod = load_script(pyfile, name)
      File "/home/user/OpenUpgrade/odoo/modules/migration.py", line 26, in load_script
        return imp.load_module(module_name, fp, fname, ('.py', 'r', imp.PY_SOURCE))
    ValueError: load_module arg#2 should be a file or None

  You need to make sure you are calling OpenUpgrade for upgrading to version 11 with python3:

  .. code-block:: bash

    $ python3 OpenUpgrade/odoo-bin --addons-path OpenUpgrade/addons --database odoo_10_migrate_to_v11 --update all --stop-after-init

python virtualenv not used in command line
------------------------------------------

  When you are using a virtualenv to start Odoo or the OpenUpgrade and you get a "No module named ..." error even after
  installing the requirements with *pip install -r OpenUpgrade/requirements.txt*

  .. code-block:: bash

    $ OpenUpgrade/odoo-bin --addons-path OpenUpgrade/addons --database odoo_10_migrate_to_v11 --update all --stop-after-init
    Traceback (most recent call last):
      File "OpenUpgrade/odoo-bin", line 5, in <module>
        import odoo
      File "/home/user/OpenUpgrade/odoo/__init__.py", line 84, in <module>
        from . import modules
      File "/home/user/OpenUpgrade/odoo/modules/__init__.py", line 8, in <module>
        from . import db, graph, loading, migration, module, registry
      File "/home/user/OpenUpgrade/odoo/modules/graph.py", line 10, in <module>
        import odoo.tools as tools
      File "/home/user/OpenUpgrade/odoo/tools/__init__.py", line 7, in <module>
        from . import pdf
      File "/home/user/OpenUpgrade/odoo/tools/pdf.py", line 4, in <module>
        from PyPDF2 import PdfFileWriter, PdfFileReader
    ModuleNotFoundError: No module named 'PyPDF2'

  You may have created the virtualenv for a python version that differs from the one used in odoo-bin.
  Call odoo-bin with your python instead:

  .. code-block:: bash

    $ python OpenUpgrade/odoo-bin --addons-path OpenUpgrade/addons --database odoo_10_migrate_to_v11 --update all --stop-after-init
