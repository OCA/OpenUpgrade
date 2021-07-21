# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def merge_priorities(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("priority"),
        "priority",
        [("1", "0"), ("2", "1"), ("3", "1")],
        table="mrp_production",
    )


def map_stock_move_line_lot_produced_ids(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET lot_id = rel.stock_production_lot_id
        FROM stock_move_line_stock_production_lot_rel rel
        JOIN stock_move_line_consume_rel rel2
            ON rel2.produce_line_id = rel.stock_move_line_id
        WHERE sml.lot_id IS NULL AND rel2.consume_line_id = sml.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO stock_move_line_consume_rel (
            produce_line_id, consume_line_id)
        SELECT rel.stock_move_line_id, sml.id
        FROM stock_move_line_stock_production_lot_rel rel
        JOIN stock_move_line sml ON (
            sml.lot_id = rel.stock_production_lot_id
            AND rel.stock_move_line_id != sml.id)
        LEFT JOIN stock_move_line_consume_rel rel2 ON (
            rel2.produce_line_id = rel.stock_move_line_id
            AND rel2.consume_line_id = sml.id)
        WHERE rel2.produce_line_id IS NULL""",
    )


def map_mrp_production_state_planned(env):
    env["mrp.production"].search([("state", "=", "planned")])._compute_state()


@openupgrade.migrate()
def migrate(env, version):
    merge_priorities(env)
    map_stock_move_line_lot_produced_ids(env)
    map_mrp_production_state_planned(env)
    openupgrade.load_data(env.cr, "mrp", "14.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, ["mrp.mrp_routing_rule", "mrp.sequence_mrp_route"]
    )
