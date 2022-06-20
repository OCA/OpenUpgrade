from openupgradelib import openupgrade


def _fill_product_template_detailed_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET detailed_type = type
        WHERE type = 'product'
        """,
    )


def _fill_stock_move_is_inventory(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_move
            SET is_inventory = True
            WHERE inventory_id IS NOT NULL;
        """,
    )


def _fill_stock_picking_type_print_label(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_picking_type
            SET print_label = True
            WHERE code = 'outgoing';
        """,
    )


def _create_default_return_type_for_all_warehouses(env):
    all_warehouses = env["stock.warehouse"].with_context(active_test=False).search([])
    for wh in all_warehouses:
        # choose the next available color for the operation types of this warehouse
        all_used_colors = [
            res["color"]
            for res in env["stock.picking.type"].search_read(
                [("warehouse_id", "!=", False), ("color", "!=", False)],
                ["color"],
                order="color",
            )
        ]
        available_colors = [zef for zef in range(0, 12) if zef not in all_used_colors]
        color = available_colors[0] if available_colors else 0

        sequence_data = wh._get_sequence_values()
        # suit for each warehouse: reception, internal, pick, pack, ship
        max_sequence = env["stock.picking.type"].search_read(
            [("sequence", "!=", False)],
            ["sequence"],
            limit=1,
            order="sequence desc",
        )
        max_sequence = max_sequence and max_sequence[0]["sequence"] or 0

        values = wh._get_picking_type_update_values()["return_type_id"]
        create_data, _ = wh._get_picking_type_create_values(max_sequence)

        values.update(create_data["return_type_id"])
        sequence = env["ir.sequence"].create(sequence_data["return_type_id"])
        values.update(
            warehouse_id=wh.id,
            color=color,
            sequence_id=sequence.id,
            sequence=max_sequence + 1,
        )
        # create return picking type
        return_type_id = env["stock.picking.type"].create(values).id
        # update return pikcing type for warehouse
        wh.write({"return_type_id": return_type_id})
        wh.out_type_id.write({"return_picking_type_id": return_type_id})
        wh.in_type_id.write({"return_picking_type_id": wh.out_type_id.id})


def _fill_stock_quant_last_inventory_date(env):
    openupgrade.logged_query(
        env.cr,
        """
            WITH sub_tmpl AS (
                SELECT sl.id as sl_id, max(sml.date) as sml_date
                FROM stock_location sl
                JOIN stock_move_line sml ON (
                    sml.company_id = sl.company_id
                    AND sml.state = 'done'
                    AND (sml.location_id = sl.id
                        OR sml.location_dest_id = sl.id))
                JOIN stock_move sm ON (sml.move_id = sm.id AND sm.is_inventory = true)
                WHERE sl.usage in ('internal', 'transit')
                GROUP BY sl.id
            )
            UPDATE stock_location sl
            SET last_inventory_date = sub_tmpl.sml_date
            FROM sub_tmpl
            WHERE sub_tmpl.sl_id = sl.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "stock", "15.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "stock",
        ["mail_template_data_delivery_confirmation"],
    )
    # try delete noupdate records
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "stock.stock_inventory_comp_rule",
            "stock.stock_inventory_line_comp_rule",
            "stock.sequence_tracking",
        ],
    )

    _fill_product_template_detailed_type(env)

    _fill_stock_move_is_inventory(env)
    _fill_stock_picking_type_print_label(env)
    _create_default_return_type_for_all_warehouses(env)
    _fill_stock_quant_last_inventory_date(env)
