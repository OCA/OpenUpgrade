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


def set_price_unit_on_stock_move_for_inventory_adjustments(cr):
    """
    In v10 when there is an inventory adjustment adding qty the price unit in
    the stock_move is null and the cost in the quant is the standard price.
    Here we align the unit_price in the stock_move to the value in the quant
    """
    openupgrade.logged_query(
        cr, """
            UPDATE stock_move sm0 SET price_unit = sq1.correct_price_unit FROM  (

		            WITH RECURSIVE next_quant(quant_id, move_id) AS (
		                SELECT quant_id, move_id FROM stock_quant_move_rel rel
		                UNION
		                SELECT rel.quant_id, nxt.move_id FROM stock_quant_move_rel rel
				    JOIN stock_quant sq ON rel.quant_id = sq.id
				    JOIN stock_move sm ON rel.move_id = sm.id
		                    JOIN next_quant nxt ON (nxt.move_id = rel.move_id)

		            ) SELECT origin_sm.id as origin_move_id,
		                           sq.cost, sq.qty,
		                           origin_sm.price_unit,
		                           sq.cost AS correct_price_unit,
		                           sl.name AS start_location, slq.name AS current_location
				    FROM next_quant rel
				    JOIN stock_quant sq ON rel.quant_id = sq.id
				    JOIN stock_move origin_sm ON rel.move_id = origin_sm.id
				    JOIN stock_location sl ON origin_sm.location_id = sl.id
				    JOIN stock_location slq ON sq.location_id = slq.id
				    WHERE origin_sm.state = 'done' AND origin_sm.location_id = sq.location_id AND
					origin_sm.state = 'done' AND
		                        sq.qty <> 0 AND
		                        sq.qty IS NOT NULL AND
					origin_sm.location_dest_id = sq.location_id AND
		                        sl.usage = 'inventory' AND
		                        (origin_sm.price_unit IS NULL OR origin_sm.price_unit = 0.0)
            ) AS SQ1 WHERE sm0.id = SQ1.origin_move_id

        """,
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    delete_quants_for_consumable(env)
    fix_act_window(env)
    set_price_unit_on_stock_move_for_inventory_adjustments(env.cr)
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
