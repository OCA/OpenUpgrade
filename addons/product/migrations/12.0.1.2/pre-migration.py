# Copyright 2018 Paul Catinean <https://github.com/PCatinean>
# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'res_partner': [
        ('create_variant', None),
    ],
    'product_attribute_price': [
        ('value_id', 'product_attribute_value_id'),
    ],
}

_model_renames = [
    ('product.attribute.line', 'product.template.attribute.line'),
    ('product.attribute.price', 'product.template.attribute.value'),
]

_table_renames = [
    ('product_attribute_line', 'product_template_attribute_line'),
    ('product_attribute_price', 'product_template_attribute_value'),
]


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
