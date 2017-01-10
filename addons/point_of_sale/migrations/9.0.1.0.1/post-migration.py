# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade

column_defaults = {
    'pos.config': [
        ('barcode_nomenclature_id', None)
    ],
    'pos.order': [
        ('session_id', None)
    ],
}


def update_barcodes_nomenclatures(env):
    # Create new barcode_nomenclature for each pos_config and create rules
    # for old fields
    cr = env.cr
    pos_configs = env['pos.config'].search([])
    for pos_config in pos_configs:
        barcode_nomenclature = env['barcode.nomenclature'].create({
            'name': pos_config.name,
            'upc_ean_conv': 'always',
            'rule_ids': [(6, 0, [1])]
        })
        old_barcode_product = openupgrade.get_legacy_name('barcode_product')
        old_barcode_cashier = openupgrade.get_legacy_name('barcode_cashier')
        old_barcode_customer = openupgrade.get_legacy_name('barcode_customer')
        old_barcode_discount = openupgrade.get_legacy_name('barcode_discount')
        old_barcode_price = openupgrade.get_legacy_name('barcode_price')
        old_barcode_weight = openupgrade.get_legacy_name('barcode_weight')
        cr.execute(
            """
            SELECT %s,%s,%s,%s,%s,%s from pos_config WHERE id = %s""" % (
                old_barcode_product, old_barcode_cashier, old_barcode_customer,
                old_barcode_discount, old_barcode_price, old_barcode_weight,
                pos_config.id,
            )
        )
        barcodes = cr.dictfetchone()
        for field, value in barcodes.iteritems():
            if not value:
                continue
            field_name = field.split('_')[-1]
            env.cr.execute(
                """INSERT INTO barcode_rule (
                    name, barcode_nomenclature_id, sequence, type, encoding,
                    pattern) VALUES (%s, %s, %s, %s, %s, %s)
                """ % (
                    field_name + 'Barcode', barcode_nomenclature.id, 50,
                    field_name, 'any', value
                )
            )
        pos_config.barcode_nomenclature_id = barcode_nomenclature.id


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.set_defaults(env.cr, env.registry, column_defaults)
    update_barcodes_nomenclatures(env)
    openupgrade.load_data(
        env.cr, 'point_of_sale', 'migrations/9.0.1.0.1/noupdate_changes.xml')
