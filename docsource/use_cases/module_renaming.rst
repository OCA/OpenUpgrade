Module Renaming
+++++++++++++++

Example
-------

From version 14.0 to version 15.0, the ``crm_iap_lead_enrich`` module
has been renamed into ``crm_iap_enrich``.

See `Full v14 Module <https://github.com/odoo/odoo/tree/14.0/addons/crm_iap_lead_enrich>`_.

See `Full v15 Module <https://github.com/odoo/odoo/tree/15.0/addons/crm_iap_enrich>`_.


Result without migration script / Expected Result
-------------------------------------------------

V14 table ``ir_module_module``
""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "state", "latest_version"

   "200", "crm_iap_lead_enrich", "installed", "14.0.1.1"

V15 table ``ir_module_module`` (Without openupgrade)
""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "state", "latest_version"

   "200", "crm_iap_lead_enrich", "to upgrade", "14.0.1.1"
   "405", "crm_iap_enrich", "uninstalled", ""


**Problem**:

- The v14 module remains in a ``to upgrade`` state.
- The v15 module has not been installed.

As a result, the models of the module have not been loaded, the related features
are not available, and the database is in a unstable state.

V15 table ``ir_module_module`` (With openupgrade)
"""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "state", "latest_version"

   "200", "crm_iap_enrich", "installed", "15.0.1.1"

Contribution to OpenUpgrade
---------------------------

apriori.py file
"""""""""""""""

The list of the renamed module is present in a ``apriori.py`` file in each version
of openupgrade.

* Until version 13, the file is present in this path:
  ``odoo/addons/openupgrade_records/lib/apriori.py``.

* from version 14.0 onwards, the file is present in this path:
  ``openupgrade_scripts/apriori.py``.

Add a key in the following dict:

.. code-block:: python

    renamed_modules = {
        "crm_iap_lead_enrich": "crm_iap_enrich",
    }

See `Full v15 apriori file <https://github.com/OCA/OpenUpgrade/blob/97491cb7d9a8ed494a49cf1db9b7fc8852aac254/openupgrade_scripts/apriori.py#L9-L27>`_.

pre-migration.py file
"""""""""""""""""""""

in the migration folder of the ``base`` module, add:

.. code-block:: python

    from odoo.addons.openupgrade_scripts.apriori import renamed_modules

    @openupgrade.migrate(use_env=False)
    def migrate(cr, version):
        openupgrade.update_module_names(cr, renamed_modules.items())

See `Full v15 base pre migration file <https://github.com/OCA/OpenUpgrade/blob/97491cb7d9a8ed494a49cf1db9b7fc8852aac254/openupgrade_scripts/scripts/base/15.0.1.3/pre-migration.py#L73>`_.

Note: The addition is done at the initialization of the OpenUpgrade Project,
for each new version. So you will generally not have to do this, as it's only OpenUpgrade maintainers that initialize the OpenUpgrade Project.

Coverage File
"""""""""""""

A coverage file is present in each version:

* Until version 13, the file is present in this path:
  ``odoo/openupgrade/doc/source/modulesXXX-YYY.rst``.

* from version 14.0 onwards, the file is present in this path:
  ``docsource/modulesXXX-YYY.rst``.

Edit this file, and add the following text:

.. code-block:: rst

    +-----------------------------------+---------+-------------------------------------------------+
    | Module                            | Status  + Extra Information                               |
    +===================================+=========+=================================================+
    +-----------------------------------+---------+-------------------------------------------------+
    | |new| crm_iap_enrich              |         | Renamed from crm_iap_lead_enrich                |
    +-----------------------------------+---------+-------------------------------------------------+
    | |del| crm_iap_lead_enrich         |         | Renamed to crm_iap_enrich                       |
    +-----------------------------------+---------+-------------------------------------------------+

Generate / Update analysis file
"""""""""""""""""""""""""""""""

As long as the renaming has not been identified, the ``upgrade_analysis.txt`` generated
at the initialization of the OpenUpgrade version is partially wrong, because openupgrade
considers that the xml_id of the module are new, while they can come from the module of
the previous version.

For the Odoo modules that are concerned by the renaming, you must update the version
analysis with the upgrade_analysis tool present in the OCA/server-tools project.

Once the analysis is done with the updated ``apriory.py`` file, the analysis
file contains correct information, and can be studied to write remaining
pre / post migration scripts.


.. code-block:: xml

    ---XML records in module 'crm_iap_enrich'---
    NEW ir.actions.server: crm_iap_enrich.action_enrich_mail [renamed from crm_iap_lead_enrich module]
    DEL ir.actions.server: crm_iap_lead_enrich.action_enrich_mail [renamed to crm_iap_enrich module]

See `Full v15 upgrade analysis file <https://github.com/OCA/OpenUpgrade/blob/97491cb7d9a8ed494a49cf1db9b7fc8852aac254/openupgrade_scripts/scripts/crm_iap_enrich/15.0.1.1/upgrade_analysis.txt>`_.

Notes
-----

* In the ``apriori.py`` file, in the ``renamed_modules`` dict, put the Odoo renaming at
  the beginning, ordered by module name, then OCA modules renaming, with the mention of
  OCA repository. Example:

.. code-block:: python

    renamed_modules = {
        # Odoo
        'crm_reveal': 'crm_iap_lead',
        'payment_ogone': 'payment_ingenico',
        # OCA/delivery-carrier
        'delivery_carrier_label_ups': 'delivery_ups_oca',
        # OCA/event
        'website_event_filter_selector': 'website_event_filter_city',
    }

* If your instance has custom modules, and if you took advantage of the migration
  to refactor these custom modules by renaming them,
  you can add the following lines at the end of this file:

.. code-block:: python

    renamed_modules.update({
        "my_obsolete_module": "my_renamed_module",
    })

(no need in this case to propose a PR to the community)
