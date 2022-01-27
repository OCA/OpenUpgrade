# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_merge_records
from psycopg2 import sql
from psycopg2.extensions import AsIs


def map_stock_rule_action(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('action'),
        'action',
        [('move', 'pull'),
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
    pull_push_rule_ids = tuple(set([r[0] for r in rules_to_merge]))
    if pull_push_rule_ids:
        openupgrade.logged_query(
            env.cr, """
            UPDATE stock_rule
            SET action = 'pull_push'
            WHERE id in %s""", (pull_push_rule_ids, ),
        )


def fill_stock_package_level(env):
    """Only stock.move.line records with package_id = result_package_id means
    that a package level should be created, as in previous version,
    result_package_id was only written when entire package was transferred.
    """
    StockPackageLevel = env['stock.package_level']
    StockMoveLine = env['stock.move.line']
    criteria = [
        'picking_id',
        'package_id',
        'result_package_id',
        'location_id',
        'location_dest_id',
    ]
    groups = StockMoveLine.read_group(
        [('result_package_id', '!=', False), ('package_id', '!=', False)],
        criteria, criteria, lazy=False,
    )
    for group in groups:
        if group['package_id'] == group['result_package_id']:
            move_lines = StockMoveLine.search(group['__domain'])
            StockPackageLevel.create({
                'package_id': group['result_package_id'][0],
                'picking_id': group['picking_id'][0],
                'location_id': group['location_id'][0],
                'location_dest_id': group['location_dest_id'][0],
                'move_line_ids': [(6, 0, move_lines.ids)]
            })


def merge_stock_putaway_product(cr):
    if openupgrade.table_exists(cr, 'stock_product_putaway_strategy'):
        column_name = openupgrade.get_legacy_name('old_strat_id')
        # first, we add the ones with product variant
        openupgrade.logged_query(cr, sql.SQL(
            """INSERT INTO stock_fixed_putaway_strat (product_id, putaway_id,
                fixed_location_id, sequence,
                create_uid, create_date, write_uid, write_date, {})
            SELECT product_product_id, putaway_id, fixed_location_id, sequence,
                create_uid, create_date, write_uid, write_date, id
            FROM stock_product_putaway_strategy
            WHERE product_product_id IS NOT NULL"""
        ).format(sql.Identifier(column_name)))
        # second, we add the ones with product product template
        openupgrade.logged_query(cr, sql.SQL(
            """INSERT INTO stock_fixed_putaway_strat (product_id, putaway_id,
                fixed_location_id, sequence,
                create_uid, create_date, write_uid, write_date, {})
            SELECT pp.id, spps.putaway_id, spps.fixed_location_id,
                spps.sequence, spps.create_uid, spps.create_date,
                spps.write_uid, spps.write_date, spps.id
            FROM stock_product_putaway_strategy spps
            JOIN product_template pt ON pt.id = spps.product_tmpl_id
            JOIN product_product pp ON pp.product_tmpl_id = pt.id
            LEFT JOIN stock_fixed_putaway_strat sfps ON (
                sfps.product_id = pp.id AND sfps.putaway_id = spps.putaway_id AND
                sfps.fixed_location_id = spps.fixed_location_id)
            WHERE sfps.putaway_id IS NULL"""
        ).format(sql.Identifier(column_name)))


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    env['stock.location']._parent_store_compute()
    map_stock_rule_action(cr)
    fill_stock_picking_type_barcode(env)
    merge_stock_location_path_stock_rule(env)
    fill_stock_package_level(env)
    merge_stock_putaway_product(cr)
    openupgrade.load_data(
        cr, 'stock', 'migrations/12.0.1.1/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'stock.stock_location_path_comp_rule',
        ],
    )
