XML-ID Renaming
+++++++++++++++

Example
-------

From version 11.0 to version 12.0, in the ``crm`` module,
the XML-ID of the ``ir.actions.act_window.view`` that target opportunities
has been renamed from ``action_crm_tag_form_view_oppor11`` (v11)
to ``crm_lead_opportunities_view_form`` (v12).

Source Code Differences
-----------------------

Version 11.0
""""""""""""

.. code-block:: xml

    <odoo>
        <record model="ir.actions.act_window.view" id="action_crm_tag_form_view_oppor11">
            <field name="sequence" eval="2"/>
            <field name="view_mode">form</field>
            <field name="view_id" ref="crm_case_form_view_oppor"/>
            <field name="act_window_id" ref="crm_lead_opportunities"/>
        </record>
    </odoo>

See `Full v11 Code Source <https://github.com/odoo/odoo/blob/84ab74c62a19d08de8b6c7c4e3f3300d7e79bcf9/addons/crm/views/crm_lead_views.xml#L869>`_.


Version 12.0
""""""""""""

.. code-block:: xml

    <odoo>
        <record id="crm_lead_opportunities_view_form" model="ir.actions.act_window.view">
            <field name="sequence" eval="2"/>
            <field name="view_mode">form</field>
            <field name="view_id" ref="crm_case_form_view_oppor"/>
            <field name="act_window_id" ref="crm_lead_opportunities"/>
        </record>
    </odoo>


See `Full v12 Code Source <https://github.com/odoo/odoo/blob/0e56e4a7bd6de42d729441a53995ddd459d5e633/addons/crm/views/crm_lead_views.xml#L980>`_.

Analysis
--------

.. code-block:: text

    ---XML records in module 'crm'---
    ...
    DEL ir.actions.act_window.view: crm.action_crm_tag_form_view_oppor11
    ...
    NEW ir.actions.act_window.view: crm.crm_lead_opportunities_view_form

See `Full v12 Analysis File <https://github.com/OCA/OpenUpgrade/blob/568c9c5c35f443df9c2d0a83b869f9fb5a6de737/addons/crm/migrations/12.0.1.0/openupgrade_analysis.txt#L33>`_.



Result without migration script / Expected Result
-------------------------------------------------

V11 table ``ir_act_window_view``
""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "create_date", "write_date"

   "28", "2020-01-02 15:23:16", "2020-01-02 15:23:16"

V12 table ``ir_act_window_view`` (Without migration script)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "create_date", "write_date"

   "35", "2023-04-02 12:00:23", "2023-04-02 12:00:23"


**Problem**:

- The previous element (id=28) has been deleted.
- A new one has been created.

As a result, all the changes done previously has been lost. (values, translations, etc...)

V12 table ``ir_act_window_view`` (With migration script)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "create_date", "write_date"

   "28", "2020-01-02 15:23:16", "2023-04-02 12:00:23"


Contribution to OpenUpgrade
---------------------------

Update ``upgrade_analysis_work.txt`` file
"""""""""""""""""""""""""""""""""""""""""

* Place side by side the two lines that correspond to the change
* Mention the operation performed, starting with ``# DONE:``

.. code-block:: text

    ---Fields in module 'crm'---
    DEL ir.actions.act_window.view: crm.action_crm_tag_form_view_oppor11
    NEW ir.actions.act_window.view: crm.crm_lead_opportunities_view_form
    # DONE: pre-migration: Renamed XML-IDs

See `Full v12 Work Analysis File <https://github.com/OCA/OpenUpgrade/blob/568c9c5c35f443df9c2d0a83b869f9fb5a6de737/addons/crm/migrations/12.0.1.0/openupgrade_analysis_work.txt#L38>`_.

Write migration Script
""""""""""""""""""""""

in the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade


    _xml_ids_renames = [
        ('crm.action_crm_tag_form_view_oppor11',
         'crm.crm_lead_opportunities_view_form'),
    ]

    @openupgrade.migrate()
    def migrate(env, version):
        openupgrade.rename_xmlids(env.cr, _xml_ids_renames)

See `Full pre migration Script <https://github.com/OCA/OpenUpgrade/blob/568c9c5c35f443df9c2d0a83b869f9fb5a6de737/addons/crm/migrations/12.0.1.0/pre-migration.py#L24>`_.


Notes
-----

* This operation is placed in the ``pre-migration.py`` step, to be executed before the
  load of the data, in the regular update process.

* In most cases, the XML-ID renaming is required because from a version to the next one,
  Odoo moves data from a module to another.

  For exemple, from 13.0 to 14.0 some data have been moved from ``sale_timesheet``
  to ``sale_project``.

  See : `Sale Project migration script <https://github.com/OCA/OpenUpgrade/blob/6fded25b7914ee3c1e5f3066252807e7f9b92cbe/openupgrade_scripts/scripts/sale_project/14.0.1.0/pre-migration.py#L1>`_.

* If the data is flagged as ``noupdate="1"`` the table after the upgrade
  (without migration script) will contains a duplicates.

  This duplicates can generate a crash of your upgrade, if some constraints are present.

  For example, the ``ir.config.parameter`` named ``mail.icp_mail_bounce_alias`` (v14) has been
  renamed into ``base.icp_mail_bounce_alias`` (v15).
  As the ``ir.config.parameter`` is created with a ``noupdate="1"`` flag AND there is
  a unicity constraint in the ``key`` field, the creation of the duplicates will fail, during the upgrade
  process.

* In the case of merging a module, the renaming is done in two steps:

  For example, the v12 module ``mrp_byproduct`` has been merged into ``mrp`` module in v13.
  The ``ir.model.access`` in v12 (``mrp_byproduct.access_mrp_subproduct_manager``) is now ``mrp.access_mrp_bom_byproduct_manager`` in v13.

  The rename is done in two steps:

    * First, at the beginning of the OpenUpgrade process, the ``apriori.py`` file is loaded,
      that indicates the merge of the module. At that step,
      ``mrp_byproduct.access_mrp_subproduct_manager`` is renamed into ``mrp.access_mrp_subproduct_manager``.

    * Then, when the ``pre-migration.py`` of the ``mrp`` module is executed,
      ``mrp.access_mrp_subproduct_manager`` is renamed into ``mrp.access_mrp_bom_byproduct_manager``.
