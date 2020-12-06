* call your odoo instance with the option ``--load=web,openupgrade_framework``

or

* add the key to your configuration file:

.. code-block:: shell

    [options]
    server_wide_modules = web,openupgrade_framework

When you load the module in either way of these ways, and you have the
`openupgrade_scripts` module in your addons path available, the
`--upgrade-path` option of Odoo will be set automatically to the location
of the OpenUpgrade migration scripts.
