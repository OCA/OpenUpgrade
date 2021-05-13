# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def create_pos_payment_methods(env):
    env["pos.config"].post_install_pos_localisation()


def create_pos_payments(env):
    env.cr.execute("""
        SELECT DISTINCT absl.id, ppm.id, absl.pos_statement_id,
            absl.name, absl.amount, absl.create_date
        FROM account_bank_statement abs
        JOIN pos_session ps ON abs.pos_session_id = ps.id
        JOIN account_bank_statement_line absl ON absl.statement_id = abs.id
        LEFT JOIN account_journal aj ON abs.journal_id = aj.id
        JOIN pos_payment_method ppm ON ppm.cash_journal_id = aj.id
        WHERE absl.pos_statement_id IS NOT NULL
    """)
    st_lines = env.cr.fetchall()
    if st_lines:
        vals_list = []
        for st_line in st_lines:
            vals = {
                'name': st_line[3],
                'pos_order_id': st_line[2],
                'amount': st_line[4],
                'payment_method_id': st_line[1],
                'payment_date': st_line[5],
            }
            vals_list += [vals]
        env['pos.payment'].create(vals_list)


def fill_stock_warehouse_pos_type_id(env):
    warehouses = env['stock.warehouse'].search([('pos_type_id', '=', False)])
    for warehouse in warehouses:
        if warehouse.get_external_id()[warehouse.id] == "stock.warehouse0":
            # If it's the main warehouse, assign the existing type
            warehouse.pos_type_id = env.ref("point_of_sale.picking_type_posout")
            continue
        color = warehouse.in_type_id.color
        sequence_data = warehouse._get_sequence_values()
        max_sequence = env['stock.picking.type'].search_read(
            [('sequence', '!=', False)], ['sequence'], limit=1,
            order='sequence desc')
        max_sequence = max_sequence and max_sequence[0]['sequence'] or 0
        create_data = warehouse._get_picking_type_create_values(max_sequence)[0]
        picking_type = "pos_type_id"
        sequence = env['ir.sequence'].sudo().create(sequence_data[picking_type])
        create_data[picking_type].update(
            warehouse_id=warehouse.id, color=color, sequence_id=sequence.id)
        warehouse[picking_type] = env['stock.picking.type'].create(
            create_data[picking_type]).id
    # Remove this to disappear XML-ID for avoiding error
    env["ir.model.data"].search([
        ("module", "=", "point_of_sale"),
        ("name", "=", "picking_type_posout"),
    ]).unlink()


@openupgrade.migrate()
def migrate(env, version):
    create_pos_payment_methods(env)
    create_pos_payments(env)
    fill_stock_warehouse_pos_type_id(env)
