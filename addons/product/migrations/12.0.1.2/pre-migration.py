# Copyright 2018 Paul Catinean <https://github.com/PCatinean>
# Copyright 2018-19 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    'product_attribute': [
        ('create_variant', None),
    ],
    'product_attribute_line_product_attribute_value_rel': [
        ('product_attribute_line_id', 'product_template_attribute_line_id'),
    ],
}

_field_renames = [
    ('product.attribute.price', 'product_attribute_price', 'value_id',
     'product_attribute_value_id'),
]

_model_renames = [
    ('product.attribute.line', 'product.template.attribute.line'),
    ('product.attribute.price', 'product.template.attribute.value'),
]

_table_renames = [
    ('product_attribute_line', 'product_template_attribute_line'),
    ('product_attribute_price', 'product_template_attribute_value'),
    ('product_attribute_line_product_attribute_value_rel',
     'product_attribute_value_product_template_attribute_line_rel'),
]

xmlid_renames = [
    ('hr_expense.cat_expense', 'product.cat_expense'),
]


def avoid_new_constraint_in_product_template_attribute_line(cr):
    # now, all attribute lines should be linked to an attribute value
    openupgrade.logged_query(
        cr, """
        DELETE FROM product_template_attribute_line line
        WHERE line.id NOT IN (
            SELECT DISTINCT product_template_attribute_line_id
            FROM product_attribute_value_product_template_attribute_line_rel
        )"""
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    avoid_new_constraint_in_product_template_attribute_line(cr)
