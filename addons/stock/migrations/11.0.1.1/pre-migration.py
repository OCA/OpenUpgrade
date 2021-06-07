# -*- coding: utf-8 -*-
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def delete_quants_for_consumable(env):
    """On v11, consumable products don't generate quants, so we can remove them
    as soon as possible for cleaning the DB and avoid other computations (like
    the merge records operation).
    """
    openupgrade.logged_query(
        env.cr, """
        DELETE FROM stock_quant sq
        USING product_product pp,
            product_template pt
        WHERE sq.product_id = pp.id
            AND pt.id = pp.product_tmpl_id
            AND pt.type = 'consu'
        """
    )


def remove_company_for_quants_in_vendor_customer(env):
    """On v11, customer or vendor location's quants do not have company
    (it is not assinged, it is related to the location) and customer
    location should not have company. In v10 is was a _company_default_get.
    We should remove the company on those in order to be aligned to the
    new flow.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_quant sq
        SET company_id = sl.company_id
        FROM stock_location sl
        WHERE sl.id = sq.location_id
            AND sl.usage in ('customer', 'supplier')
            AND sq.company_id != sl.company_id
        """
    )


def fix_act_window(env):
    """Action window with XML-ID 'stock.action_procurement_compute' has
    set src_model='procurement.order', and this will provoke an error as
    new definition doesn't overwrite this field. We empty that value before
    that happens. The source of this assignation is not clear, but it doesn't
    hurt any way.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_act_window iaw
        SET src_model = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = iaw.id
            AND imd.module = 'stock'
            AND imd.name = 'action_procurement_compute'""",
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    delete_quants_for_consumable(env)
    remove_company_for_quants_in_vendor_customer(env)
    fix_act_window(env)
    openupgrade.update_module_moved_fields(
        env.cr, 'stock.move', ['has_tracking'], 'mrp', 'stock',
    )
    openupgrade.update_module_moved_fields(
        env.cr, 'stock.move', ['quantity_done'], 'mrp', 'stock',
    )
    openupgrade.rename_fields(
        env, [
            ('stock.quant', 'stock_quant', 'qty', 'quantity'),
        ]
    )
    openupgrade.copy_columns(
        env.cr, {
            'stock_picking': [
                ('state', None, None),
            ],
        },
    )
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('state'), 'state',
        [('partially_available', 'assigned')], table='stock_picking',
    )
    openupgrade.add_fields(
        env, [
            ('reference', 'stock.move', 'stock_move', 'char', False, 'stock'),
            ('scheduled_date', 'stock.picking', 'stock_picking', 'date', False,
             'stock'),
        ],
    )
    openupgrade.set_xml_ids_noupdate_value(
        env, 'stock', [
            'barcode_rule_location',
            'barcode_rule_lot',
            'barcode_rule_package',
            'barcode_rule_weight_three_dec',
        ], True)
