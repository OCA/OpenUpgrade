# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # account.journal
    'point_of_sale.pos_sale_journal',
    # ir.sequence
    'point_of_sale.seq_picking_type_posout',
]


def fill_pos_config_default_cashbox_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE pos_config pc
        SET default_cashbox_id = absc.id
        FROM account_cashbox_line acl
        JOIN account_bank_statement_cashbox absc ON acl.cashbox_id = absc.id
        WHERE acl.{} = pc.id
        """.format(openupgrade.get_legacy_name('default_pos_id'))
    )


def fill_pos_config_amount_authorized_diff(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE pos_config pc
        SET amount_authorized_diff = aj.{amount}
        FROM account_bank_statement abs
        JOIN account_journal aj ON abs.journal_id = aj.id
        JOIN pos_session ps ON abs.pos_session_id = ps.id
        WHERE ps.config_id = pc.id AND pc.amount_authorized_diff IS NULL
            AND aj.{amount} IS NOT NULL
        """.format(amount=openupgrade.get_legacy_name('amount_authorized_diff'))
    )


def fill_pos_session_move_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE pos_session ps
        SET move_id = po.{move}
        FROM pos_order po
        WHERE po.session_id = ps.id AND po.{move} IS NOT NULL
            AND ps.move_id IS NULL AND ps.state = 'closed'
        """.format(move=openupgrade.get_legacy_name('account_move'))
    )


def fill_pos_order_account_move(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE pos_order po
        SET account_move = am.id
        FROM account_invoice ai
        JOIN account_move am ON am.old_invoice_id = ai.id
        WHERE po.{} = ai.id
        """.format(openupgrade.get_legacy_name('invoice_id'))
    )


def fill_pos_config_barcode_nomenclature_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE pos_config pc
        SET barcode_nomenclature_id = rc.nomenclature_id
        FROM res_company rc
        WHERE pc.company_id = rc.id AND pc.barcode_nomenclature_id IS NULL
        """,
    )


def fill_pos_config_module_pos_hr(env):
    if openupgrade.table_exists(env.cr, 'hr_employee'):
        openupgrade.logged_query(
            env.cr, """
            UPDATE pos_config SET module_pos_hr = TRUE""",
        )


def delete_pos_order_line_with_empty_order_id(env):
    openupgrade.logged_query(
        env.cr, "DELETE FROM pos_order_line WHERE order_id IS NULL",
    )


def fill_stock_warehouse_pos_type_id(env):
    warehouses = env['stock.warehouse'].search([('pos_type_id', '=', False)])
    for warehouse in warehouses:
        all_used_colors = [res['color'] for res in env[
            'stock.picking.type'].search_read(
            [('warehouse_id', '!=', False), ('color', '!=', False)],
            ['color'], order='color')]
        available_colors = [
            zef for zef in range(0, 12) if zef not in all_used_colors]
        color = available_colors[0] if available_colors else 0
        sequence = env['ir.sequence'].sudo().create({
            'name': warehouse.name + ' ' + 'Picking POS',
            'prefix': warehouse.code + '/POS/',
            'padding': 5,
            'company_id': warehouse.company_id.id,
        })
        pos_type = env['stock.picking.type'].create({
            'name': 'PoS Orders',
            'code': 'outgoing',
            'default_location_src_id': warehouse.lot_stock_id.id,
            'default_location_dest_id': env.ref(
                'stock.stock_location_customers').id,
            'sequence': sequence.id,
            'sequence_code': 'POS',
            'company_id': warehouse.company_id.id,
            'warehouse_id': warehouse.id,
            'color': color,
        })
        warehouse.write({'pos_type_id': pos_type.id})


@openupgrade.migrate()
def migrate(env, version):
    fill_pos_config_default_cashbox_id(env)
    fill_pos_config_amount_authorized_diff(env)
    fill_pos_session_move_id(env)
    fill_pos_order_account_move(env)
    fill_pos_config_barcode_nomenclature_id(env)
    fill_pos_config_module_pos_hr(env)
    delete_pos_order_line_with_empty_order_id(env)
    fill_stock_warehouse_pos_type_id(env)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'point_of_sale', 'migrations/13.0.1.0.1/noupdate_changes.xml')
