# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('pos.config', 'pos_config', 'iface_invoicing', 'module_account'),
]

xmlid_renames = [
    ('point_of_sale.access_product_uom_manager',
     'point_of_sale.access_uom_uom_manager'),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    # Try to put this data here instead through noupdate records, as it can
    # fail due to stock moves already done on the product
    try:
        with cr.savepoint():
            env.ref('product_product_consumable').write({
                "uom_po_id": env.ref("uom.product_uom_unit"),
                "uom_id": env.ref("uom.product_uom_unit"),
            })
    except Exception:
        pass
