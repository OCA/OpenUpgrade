# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

RENAMED_COLUMNS = {
    'stock_picking': [
        ('weight_uom_id', None),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr, 'product.template', ['hs_code'], 'delivery', 'delivery_hs_code'
    )
    openupgrade.update_module_moved_fields(
        env.cr, 'product.product', ['hs_code'], 'delivery', 'delivery_hs_code',
    )
    openupgrade.rename_columns(env.cr, RENAMED_COLUMNS)
    openupgrade.delete_records_safely_by_xml_id(
        env, ['delivery.mail_template_data_delivery_notification'],
    )
