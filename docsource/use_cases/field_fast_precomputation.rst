Field Fast Precomputation
+++++++++++++++++++++++++

Example
-------

From version 14.0 to version 15.0, in the ``product`` module,
a new field ``value_count`` appeared on the model ``product.template.attribute.line``.
This is a simple field that stores the amount of ``value_ids``
associated with each element.

Source Code Differences
-----------------------

Version 14.0
""""""""""""

.. code-block:: python

    class ProductTemplateAttributeLine(models.Model):
        _name = "product.template.attribute.line"

        value_ids = fields.Many2many(
            comodel_name="product.attribute.value",
            relation="product_attribute_value_product_template_attribute_line_rel"
        )

See `Full v14 Code Source <https://github.com/odoo/odoo/blob/8b522e5c4b7ef406446596b719be84692a712c44/addons/product/models/product_attribute.py#LL165-L179>`_.


Version 15.0
""""""""""""

.. code-block:: python

    class ProductTemplateAttributeLine(models.Model):
        _name = "product.template.attribute.line"

        value_ids = fields.Many2many(
            comodel_name="product.attribute.value",
            relation="product_attribute_value_product_template_attribute_line_rel"
        )
        value_count = fields.Integer(
            compute="_compute_value_count",
            store=True,
        )

    @api.depends("value_ids")
    def _compute_value_count(self):
        for record in self:
            record.value_count = len(record.value_ids)

See `Full v15 Code Source <https://github.com/odoo/odoo/blob/2f817a7b36cc7e5ab235829eecd61a1d71ce546e/addons/product/models/product_attribute.py#LL189-L209>`_.

Analysis
--------

.. code-block:: text

    ---Fields in module 'product'---

    product      / product.template.attribute.line / value_count (integer):
        NEW isfunction: function, stored

See `Full v15 Analysis File <https://github.com/OCA/OpenUpgrade/blob/97491cb7d9a8ed494a49cf1db9b7fc8852aac254/openupgrade_scripts/scripts/product/15.0.1.2/upgrade_analysis.txt#L16>`_.



Result without migration script / Expected Result
-------------------------------------------------

The new field will be computed, by the ORM.
So in absolute terms, there is nothing to do.
However, the calculation will be performed for all the rows of the table.
If the table contains a very large amount of data, the calculation can be slow:
Indeed, even if the ORM contains some prefetch system for reading the data,
the writing will be done item by item, via an SQL request of the UPDATE type,
which is not at all optimized, and will generate a (quasi) linear type of time complexity.

See : https://en.wikipedia.org/wiki/Time_complexity#Linear_time

As a result, some compute on huge database can take hours, or days, or worse,
generate an insufficient memory error, which stops the migration.

These inconveniences obviously depend on the size of the table in question
and the power and the configuration of the server that is performing the migration.

Contribution to OpenUpgrade
---------------------------

Update ``upgrade_analysis_work.txt`` file
"""""""""""""""""""""""""""""""""""""""""

Add a comment after the line:

.. code-block:: text

    product      / product.template.attribute.line / value_count (integer):
        NEW isfunction: function, stored
    # DONE: pre-migration: fast computed value_count

See `Full v15 Work Analysis File <https://github.com/OCA/OpenUpgrade/blob/97491cb7d9a8ed494a49cf1db9b7fc8852aac254/openupgrade_scripts/scripts/product/15.0.1.2/upgrade_analysis_work.txt#LL32-L33>`_.

Write migration Script
""""""""""""""""""""""

in the ``pre-migration.py`` script add:

.. code-block:: python

    from openupgradelib import openupgrade

    def compute_product_template_attribute_line_value_count(env):
        openupgrade.add_fields(env, [(
            "value_count",                      # Field name
            "product.template.attribute.line",  # Model name
            "product_template_attribute_line",  # Table name
            "integer",                          # Odoo Field type (in lower case)
            False,                              # [Optional] SQL type (if custom fields)
            "product",                          # Module name
            False,                              # [Optional] Default value
        )])

        openupgrade.logged_query(
            env.cr,
            """
            UPDATE product_template_attribute_line al
            SET value_count = (
                SELECT COUNT(*)
                FROM product_attribute_value_product_template_attribute_line_rel
                WHERE product_template_attribute_line_id = al.id
            )""",
        )

    @openupgrade.migrate()
    def migrate(env, version):
        compute_product_template_attribute_line_value_count(env)

See `Full V15 pre migration Script <https://github.com/OCA/OpenUpgrade/blob/97491cb7d9a8ed494a49cf1db9b7fc8852aac254/openupgrade_scripts/scripts/product/15.0.1.2/pre-migration.py#LL4-L25>`_.

See `Full add_fields specification <https://github.com/OCA/openupgradelib/blob/master/openupgradelib/openupgrade.py>`_.

Notes
-----

* these scripts are about optimization.
  As a contributor of openupgrade for a module,
  if you do not have a problem of excessive duration,
  you can propose migration scripts _without_ such optimizations,
  especially when the SQL queries are complex to write.

  Another contributor can always propose a PR for performance improvement,
  if he faces this problem.