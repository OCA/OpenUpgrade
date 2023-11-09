Required Knowledge
==================

To Use Openupgrade
------------------

* you should be able to launch an instance of Odoo on your local PC,
  or on your server, **for each version of your migration**.
* You should know how to get `openupgradelib`, obtained from the source repository, installed in your Python environment that is going to run the instance.
* You should know how to invoke the odoo executable, injecting arguments for loading server wide modules and migrations path.
  For example, if you're migrating from version 12.0 to 16.0,
  you should be able to launch Odoo versions 13.0, 14.0, 15.0 and 16.0.

* If you're migrating to a recent version,
  you'll certainly have to reference numerous open pull requests on OCA/OpenUpgrade,
  for the modules installed on your instance.
  In this case, using the `gitaggregate <https://pypi.org/project/git-aggregator>`_
  tool greatly facilitates the management of these numerous pull requests.

To develop Openupgrade Scripts
------------------------------

- If you want to develop migration scripts for a given module, you need to have
  complete functional (and technical) knowledge of this module.
  For example, to develop migration scripts for `account` module from version 12.0
  to 13.0, you need to master how account is working in version 12.0 and how
  account is working in version 13.0.

- Knowledge of SQL is a must if you need to write fast queries on huge amounts of data.

- you need to have a good understanding of the functions provided
  by the `openupgradelib <https://oca.github.io/openupgradelib/>`_ library.
