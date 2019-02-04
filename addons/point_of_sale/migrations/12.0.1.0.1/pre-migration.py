# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('pos.config', 'pos_config', 'iface_invoicing', 'module_account'),
]

xmlid_renames = [
    ('product.product_uom_categ_unit', 'uom.product_uom_categ_unit'),
    ('point_of_sale.access_product_uom_manager',
     'point_of_sale.access_uom_uom_manager'),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
