Module Merging
++++++++++++++

Example
-------

From version 15.0 to version 16.0, the ``fetchmail_outlook`` module
has been merged into ``microsoft_outlook``.

See `According Odoo Pull Request <https://github.com/odoo/odoo/pull/88215>`_.


Result without migration script / Expected Result
-------------------------------------------------

V15 table ``ir_module_module``
""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "state", "latest_version"

   "200", "fetchmail_outlook", "installed", "15.0.1.0"
   "304", "microsoft_outlook", "installed", "15.0.1.0"

V16 table ``ir_module_module`` (Without openupgrade)
""""""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "state", "latest_version"

   "200", "fetchmail_outlook", "to upgrade", "15.0.1.0"
   "304", "microsoft_outlook", "installed", "16.0.1.0"

**Problem**:

- The v15 module remains in a ``to upgrade`` state.

As a result:

- the data will be recreated instead of having their xml_id renamed
- the database is in a unstable state.

V16 table ``ir_module_module`` (With openupgrade)
"""""""""""""""""""""""""""""""""""""""""""""""""

.. csv-table::
   :header: "id", "name", "state", "latest_version"

   "304", "microsoft_outlook", "installed", "16.0.1.0"

Contribution to OpenUpgrade
---------------------------

apriori.py file
"""""""""""""""

The list of the merged modules is present in a ``apriori.py`` file in each version
of openupgrade.

* Until version 13, the file is present in this path:
  ``odoo/addons/openupgrade_records/lib/apriori.py``.

* from version 14.0 onwards, the file is present in this path:
  ``openupgrade_scripts/apriori.py``.

Add a key in the following dict:

.. code-block:: python

    merged_modules = {
        "fetchmail_outlook": "microsoft_outlook",
    }

See `Full v16 apriori file <https://github.com/OCA/OpenUpgrade/blob/41b843404bd454051f4115da87eb39b4f1c5e5b0/openupgrade_scripts/apriori.py#L37>`_.

pre-migration.py file
"""""""""""""""""""""

in the migration folder of the ``base`` module, add:

.. code-block:: python

    from odoo.addons.openupgrade_scripts.apriori import merged_modules

    @openupgrade.migrate(use_env=False)
    def migrate(cr, version):
        openupgrade.update_module_names(
            cr,
            merged_modules.items(),
            merge_modules=True,
        )

See `Full v16 base pre migration file <https://github.com/OCA/OpenUpgrade/blob/5f341b7f80b66b06714a257237f4c76c5141983d/openupgrade_scripts/scripts/base/15.0.1.3/pre-migration.py#L74>`_.

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
    | |del| fetchmail_outlook           | Done    | Merged into microsoft_outlook.                  |
    +-----------------------------------+---------+-------------------------------------------------+


Notes
-----

* In the ``apriori.py`` file, in the ``merged_modules`` dict, put the Odoo renaming at
  the beginning, ordered by module name, then OCA modules renaming, with the mention of
  OCA repository. Example:

.. code-block:: python

    merged_modules = {
        # odoo
        "account_edi_facturx": "account_edi_ubl_cii",
        "account_edi_ubl": "account_edi_ubl_cii",
        "website_sale_gift_card": "website_sale_loyalty",
        # OCA/account-financial-tools
        "account_balance_line": "account",
        "account_move_force_removal": "account",
    }

* If your instance has custom modules, and if you took advantage of the migration
  to refactor these custom modules by merging them,
  you can add the following lines at the end of this file:

.. code-block:: python

    merged_modules.update({
        "my_obsolete_module": "my_main_module",
    })

(no need in this case to propose a PR to the community)
