# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_merge_records
from psycopg2.extensions import AsIs


def map_stock_rule_action(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('action'),
        'action',
        [('move', 'pull_push'),
         ],
        table='stock_rule', write='sql')


def fill_stock_picking_type_barcode(env):
    picking_types = env['stock.picking.type'].with_context(
        active_test=False).search([('code', '!=', False),
                                   (['warehouse_id', '!=', False])])
    installed_langs = env['res.lang'].search([])  # search only active
    for lang in installed_langs:
        default_names_dict = {
            env['ir.translation']._get_source(
                name=False, types='code', lang=lang.code, source='Receipts',
            ): '-RECEIPTS',
            env['ir.translation']._get_source(
                name=False, types='code', lang=lang.code,
                source='Delivery Orders',
            ): '-DELIVERY',
            env['ir.translation']._get_source(
                name=False, types='code', lang=lang.code, source='Pack',
            ): '-PACK',
            env['ir.translation']._get_source(
                name=False, types='code', lang=lang.code, source='Pick',
            ): '-PICK',
            env['ir.translation']._get_source(
                name=False, types='code', lang=lang.code,
                source='Internal Transfers',
            ): '-INTERNAL',
        }
        for picking_type in picking_types:
            if picking_type.name in default_names_dict:
                picking_type.barcode = picking_type.warehouse_id.code.replace(
                    " ", "").upper() + default_names_dict[picking_type.name]


def merge_stock_location_path_stock_rule(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_rule (name, active, action, sequence, company_id,
            location_id, location_src_id, route_id, procure_method,
            route_sequence, picking_type_id, delay, propagate, warehouse_id,
            auto, create_uid, create_date, write_uid, write_date, %s)
        SELECT name, active, 'push' AS action, sequence, company_id,
            location_dest_id, location_from_id, route_id,
            'make_to_stock' AS procure_method, route_sequence,
            picking_type_id, delay, propagate, warehouse_id, auto,
            create_uid, create_date, write_uid, write_date, id
        FROM stock_location_path
        """, (AsIs(openupgrade.get_legacy_name('loc_path_id')), ),
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data imd
        SET model = 'stock.rule', res_id = sr.id
        FROM stock_rule sr
        WHERE imd.res_id = sr.%s AND model = 'stock.location.path'
        """, (AsIs(openupgrade.get_legacy_name('loc_path_id')), ),
    )
    env.cr.execute(
        """
        SELECT DISTINCT sm.rule_id, sr.id
        FROM stock_move sm
        INNER JOIN stock_rule sr ON sm.%s = sr.%s
        WHERE sr.%s IS NOT NULL AND sm.rule_id IS NOT NULL
        """, (
            AsIs(openupgrade.get_legacy_name('push_rule_id')),
            AsIs(openupgrade.get_legacy_name('loc_path_id')),
            AsIs(openupgrade.get_legacy_name('loc_path_id')),
        ),
    )
    rules_to_merge = env.cr.fetchall()
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET rule_id = sr.id
        FROM stock_rule sr
        WHERE sm.%s = sr.%s
            AND sr.%s IS NOT NULL AND sm.rule_id IS NULL
        """, (
            AsIs(openupgrade.get_legacy_name('push_rule_id')),
            AsIs(openupgrade.get_legacy_name('loc_path_id')),
            AsIs(openupgrade.get_legacy_name('loc_path_id')),
        ),
    )
    for row in rules_to_merge:
        openupgrade_merge_records.merge_records(
            env, 'stock.rule',
            [row[1]],
            row[0],
        )


def merge_stock_putaway_strategy_product(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_fixed_putaway_strat (product_id, putaway_id,
            fixed_location_id, sequence, create_uid,
            create_date, write_uid, write_date, %s)
        SELECT product_product_id, putaway_id, fixed_location_id, sequence,
            create_uid, create_date, write_uid, write_date, id
        FROM stock_product_putaway_strategy
        """, (AsIs(openupgrade.get_legacy_name('putaway_strategy_id')), ),
    )


def fill_stock_package_level(env):
    all_moves = env['stock.move'].search([])
    all_pickings = env['stock.picking'].search([])

    # case 1:
    moves = all_moves.filtered(lambda m: m.state == 'assigned')
    for move in moves:
        move.mapped('picking_id')._check_entire_pack()

    # case 2:
    pickings = all_pickings.filtered(
        lambda p: p.state not in ('done', 'cancel'))
    for picking in pickings:
        move_line_ids = picking.move_line_ids.filtered(
            lambda ml: ml.qty_done > 0 and ml.result_package_id)
        if move_line_ids and len(
                move_line_ids.mapped('location_dest_id')) == 1:
            package = move_line_ids.result_package_id
            env['stock.package_level'].create({
                'package_id': package.id,
                'picking_id': picking.id,
                'location_id': False,
                'location_dest_id': move_line_ids.mapped(
                    'location_dest_id').id,
                'move_line_ids': [(6, 0, move_line_ids.ids)]
            })

    # case 3:
    moves = all_moves.filtered(
        lambda m: m.picking_id and m.state not in ('done', 'cancel'))
    for move in moves:
        move.mapped('package_level_id').write({
            'picking_id': move.picking_id.id,
        })

    # case 4:
    moves = all_moves.filtered(lambda m: m.state == 'assigned')
    moves.mapped('package_level_id').write({'is_done': True})


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    env['stock.location']._parent_store_compute()
    map_stock_rule_action(cr)
    fill_stock_picking_type_barcode(env)
    merge_stock_location_path_stock_rule(env)
    if openupgrade.table_exists(cr, 'stock_product_putaway_strategy'):
        merge_stock_putaway_strategy_product(env)
    fill_stock_package_level(env)
    openupgrade.load_data(
        cr, 'stock', 'migrations/12.0.1.1/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'stock.stock_location_path_comp_rule',
        ],
    )
