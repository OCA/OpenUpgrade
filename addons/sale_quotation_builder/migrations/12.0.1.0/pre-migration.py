# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('product.template', 'product_template',
     'quote_description', 'quotation_only_description'),
]

xmlid_renames = [
    ('sale_quotation_builder.website_quote_template_default',
     'sale_quotation_builder.sale_order_template_default'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
