Noupdate XML entry Changed
++++++++++++++++++++++++++

Rational
++++++++

When Odoo updates a module, it will reload all the entries described in XML (or CSV) files, excepted
the entries flagged as ``noupdate="1"``.

Between 2 major Odoo release, some "no updatable" entries changed.

When Openupgrade Maintainers initialize the project for a new release, a new file
is created for each module, named ``noupdate_changes.xml``.
It will contain all the changes between the two versions for the "no updatable" entries.

Source Code Differences
-----------------------

Version 14.0
""""""""""""

In : ``odoo/addons/base/security/base_security.xml``

.. code-block:: xml

    <odoo noupdate="1">
        <record model="ir.rule" id="ir_default_system_rule">
            <field name="name">Defaults: alter all defaults</field>
            <field name="model_id" ref="model_ir_default"/>
            <field name="domain_force">[(1,'=',1)]</field>
            <field name="groups" eval="[(4, ref('base.group_system'))]"/>
            <field name="perm_read" eval="False"/>
        </record>
    </odoo>

See `Full v14 Code Source of base_security <https://github.com/odoo/odoo/blob/194e57355470565cd3b7a62f74fe93cfb87c06e9/odoo/addons/base/security/base_security.xml#LL44C1-L50C18>`_.

And in : ``odoo/addons/base/data/report_paperformat_data.xml``

.. code-block:: xml

    <odoo noupdate="1">

        <record id="paperformat_batch_deposit" model="report.paperformat">
            <field name="name">US Batch Deposit</field>
            <field name="default" eval="False" />
            <field name="format">Letter</field>
            <field name="page_height">0</field>
            <field name="page_width">0</field>
            <field name="orientation">Portrait</field>
            <field name="margin_top">15</field>
            <field name="margin_bottom">10</field>
            <field name="margin_left">10</field>
            <field name="margin_right">10</field>
            <field name="header_line" eval="False" />
            <field name="header_spacing">0</field>
            <field name="dpi">90</field>
        </record>

    </odoo>

See `Full v14 Code Source of report_paperformat_data <https://github.com/odoo/odoo/blob/194e57355470565cd3b7a62f74fe93cfb87c06e9/odoo/addons/base/data/report_paperformat_data.xml#LL36C1-L50C18>`_.

Version 15.0
""""""""""""

* In : ``odoo/addons/base/security/base_security.xml``

.. code-block:: xml

    <odoo noupdate="1">
        <record model="ir.rule" id="ir_default_system_rule">
            <field name="name">Defaults: alter all defaults</field>
            <field name="model_id" ref="model_ir_default"/>
            <field name="domain_force">[(1,'=',1)]</field>
            <field name="groups" eval="[Command.link(ref('base.group_system'))]"/>
            <field name="perm_read" eval="False"/>
        </record>
    </odoo>

See `Full v15 Code Source of base_security <https://github.com/odoo/odoo/blob/aa482513a5c520ec0d650eab8677378c116127a3/odoo/addons/base/security/base_security.xml#LL44C1-L50C18>`_.

* In : ``odoo/addons/base/data/report_paperformat_data.xml``

.. code-block:: xml

    <odoo noupdate="1">

        <record id="paperformat_batch_deposit" model="report.paperformat">
            <field name="name">US Batch Deposit</field>
            <field name="default" eval="False" />
            <field name="format">Letter</field>
            <field name="page_height">0</field>
            <field name="page_width">0</field>
            <field name="orientation">Portrait</field>
            <field name="margin_top">15</field>
            <field name="margin_bottom">30</field>
            <field name="margin_left">10</field>
            <field name="margin_right">10</field>
            <field name="header_line" eval="False" />
            <field name="header_spacing">15</field>
            <field name="dpi">90</field>
        </record>

    </odoo>

See `Full v15 Code Source of report_paperformat_data <https://github.com/odoo/odoo/blob/aa482513a5c520ec0d650eab8677378c116127a3/odoo/addons/base/data/report_paperformat_data.xml#LL36C1-L50C18>`_.


noupdate_changes.xml File
-------------------------

For the two elements mentioned above, here is what the file contains

.. code-block:: xml

    <odoo>

        <record id="ir_default_system_rule" model="ir.rule">
            <field name="groups" eval="[Command.link(ref('base.group_system'))]"/>
        </record>

        <record id="paperformat_batch_deposit" model="report.paperformat">
            <field name="header_spacing">15</field>
            <field name="margin_bottom">30</field>
        </record>

    </odoo>

We can see that:

* 2 values changed for the paperformat ``paperformat_batch_deposit``.

* A changed is mentionned for the rule ``ir_default_system_rule``. however, nothing changed
  and it is only a syntaxic changes.
  ``[(4, ref('base.group_system'))]`` is equivalent to ``[Command.link(ref('base.group_system'))]``


Result without migration script / Expected Result
-------------------------------------------------

V14 table ``report_paperformat``
""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "header_spacing", "margin_bottom"

   "28", "US Batch Deposit", "0", "10"

V15 table ``report_paperformat`` (Without migration script)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", header_spacing", "margin_bottom"

   "28", "US Batch Deposit", "0", "10"

**Problem**:

- The paperformat doesn't contains the new default values.

V12 table ``ir_act_window_view`` (With migration script)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", header_spacing", "margin_bottom"

   "28", "US Batch Deposit", "15", "30"


Contribution to OpenUpgrade
---------------------------

Update ``noupdate_changes.xml`` file
""""""""""""""""""""""""""""""""""""

Open the file and for each item, try to know
if it is a real change (as in the case of the ``report.paperformat``),
or a false positive (as in the case of the ``ir.rule``)

Then comment all the false positives elements.

.. code-block:: xml

    <odoo>

        <!--
        <record id="ir_default_system_rule" model="ir.rule">
            <field name="groups" eval="[Command.link(ref('base.group_system'))]"/>
        </record>
        -->

        <record id="paperformat_batch_deposit" model="report.paperformat">
            <field name="header_spacing">15</field>
            <field name="margin_bottom">30</field>
        </record>

    </odoo>

See `Full noupdate_changes file for base module between v14 et v15 <https://github.com/OCA/OpenUpgrade/blob/171db072829c011576da50994055826afd7f5cab/openupgrade_scripts/scripts/base/15.0.1.3/noupdate_changes.xml>`_.


Write migration Script
""""""""""""""""""""""

in the ``post-migration.py`` script, add:

.. code-block:: python

        from openupgradelib import openupgrade


        @openupgrade.migrate()
        def migrate(env, version):
            openupgrade.load_data(env.cr, "base", "15.0.1.3/noupdate_changes.xml")

See `Full post migration Script <https://github.com/OCA/OpenUpgrade/blob/171db072829c011576da50994055826afd7f5cab/openupgrade_scripts/scripts/base/15.0.1.3/post-migration.py>`_.

Notes
-----

* For some people, resetting to the new defaults may not be desirable.
  In this case you will have to change the item to the previous values after the migration.

* If the field whose value has changed was translatable,
  then changing the value will not reset the translation(s),
  For exemple, for the ``mail.template`` named ``project.mail_template_data_project_task``.

  See `Full noupdate_changes file <https://github.com/OCA/OpenUpgrade/blob/171db072829c011576da50994055826afd7f5cab/openupgrade_scripts/scripts/project/15.0.1.2/noupdate_changes.xml#L3-L16>`_.

  In that case, delete the translation:

  .. code-block:: python

        from openupgradelib import openupgrade


        @openupgrade.migrate()
        def migrate(env, version):
            openupgrade.load_data(env.cr, "project", "15.0.1.2/noupdate_changes.xml")
            openupgrade.delete_record_translations(env.cr, "project", ["mail_template_data_project_task"])


  See `Full post migration file of the project module <https://github.com/OCA/OpenUpgrade/blob/171db072829c011576da50994055826afd7f5cab/openupgrade_scripts/scripts/project/15.0.1.2/post-migration.py#L80-L88>`_.