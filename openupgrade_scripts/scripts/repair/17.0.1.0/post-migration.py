# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_product_template_create_repair(env):
    # If fees where created for some service,
    # they should create repair orders automatically
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET create_repair = TRUE
        FROM repair_fee rf
        JOIN product_product pp ON rf.product_id = pp.id
        WHERE pp.product_tmpl_id = pt.id""",
    )


def fill_stock_move_repair_lines(env):
    # Insert moves for repairs lines not done yet
    openupgrade.logged_query(
        env.cr,  # TODO: to complete
        """
        INSERT INTO stock_move (old_repair_line_id,
        create_uid, create_date, write_uid, write_date,
        repair_id, repair_line_type, ...
        )
        SELECT id, create_uid, create_date, write_uid, write_date,
        repair_id, type as repair_line_type, ...
        FROM repair_line rl
        WHERE rl.move_id IS NULL AND rl.type IS NOT NULL
        """,
    )


def create_default_repair_type_for_all_warehouses(env):
    # method mainly based on _create_or_update_sequences_and_picking_types()
    all_warehouses = env["stock.warehouse"].with_context(active_test=False).search([])
    for wh in all_warehouses:
        # choose the next available color for the operation types of this warehouse
        all_used_colors = [
            res["color"]
            for res in env["stock.picking.type"]
            .with_context(active_test=False)
            .search_read(
                [("warehouse_id", "!=", False), ("color", "!=", False)],
                ["color"],
                order="color",
            )
        ]
        available_colors = [zef for zef in range(0, 12) if zef not in all_used_colors]
        color = available_colors[0] if available_colors else 0
        sequence_data = wh._get_sequence_values()
        # suit for each warehouse: reception, internal, pick, pack, ship
        max_sequence = (
            env["stock.picking.type"]
            .with_context(active_test=False)
            .search_read(
                [("sequence", "!=", False)],
                ["sequence"],
                limit=1,
                order="sequence desc",
            )
        )
        max_sequence = max_sequence and max_sequence[0]["sequence"] or 0
        values = wh._get_picking_type_update_values()["repair_type_id"]
        create_data, _ = wh._get_picking_type_create_values(max_sequence)
        values.update(create_data["repair_type_id"])
        sequence = env["ir.sequence"].create(sequence_data["repair_type_id"])
        values.update(
            warehouse_id=wh.id,
            color=color,
            sequence_id=sequence.id,
            sequence=max_sequence + 1,
            company_id=wh.company_id.id,
            active=wh.active,
        )
        # create repair picking type
        repair_type_id = env["stock.picking.type"].create(values).id
        # update repair picking type for warehouse
        wh.write({"repair_type_id": repair_type_id})


@openupgrade.migrate()
def migrate(env, version):
    # fill_stock_move_repair_lines_and_fees(env)
    fill_product_template_create_repair(env)
    create_default_repair_type_for_all_warehouses(env)
    openupgrade.load_data(env, "repair", "17.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "repair.repair_fee_rule",
            "repair.repair_line_rule",
            "repair.seq_repair",
            "repair.mail_template_repair_quotation",
        ],
    )
