# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(
        env.cr, {'pos_config': [('iface_tax_included', None)]})
    openupgrade.add_fields(env, [
        ('customer_facing_display_html', 'pos.config', 'pos_config', 'html',
         False, 'point_of_sale'),
    ])
    openupgrade.set_xml_ids_noupdate_value(
        env, 'point_of_sale', [
            'barcode_rule_cashier',
            'barcode_rule_client',
            'barcode_rule_discount',
            'barcode_rule_price_two_dec',
        ], True)
