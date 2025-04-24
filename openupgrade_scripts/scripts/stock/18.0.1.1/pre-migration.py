# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_field_renames = [
    ("stock.move", "stock_move", "location_dest_id", "location_final_id"),
    (
        "stock.warehouse.orderpoint",
        "stock_warehouse_orderpoint",
        "qty_to_order",
        "qty_to_order_manual",
    ),
]

_xmlid_renames = [
    ("stock.stock_location_inter_wh", "stock.stock_location_inter_company"),
]

_new_columns = [
    ("product.template", "is_storable", "boolean", False),
    ("stock.move", "location_dest_id", "many2one"),
    ("stock.rule", "location_dest_from_rule", "boolean", False),
    ("stock.picking.type", "move_type", "selection", "direct"),
    ("stock.putaway.rule", "sublocation", "selection", "no"),
]


def fill_product_template_is_storable(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET is_storable = TRUE, type = 'consu'
        WHERE type = 'product'""",
    )


def fill_stock_move_location_dest_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm2
        SET location_dest_id = COALESCE(sp.location_dest_id,
            spt.default_location_dest_id, sm.location_final_id)
        FROM stock_move sm
        LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
        LEFT JOIN stock_picking_type spt ON sm.picking_type_id = spt.id
        WHERE sm2.id = sm.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_rule sr
        SET location_dest_from_rule = TRUE
        FROM stock_move sm
        WHERE sm.rule_id = sr.id
            AND sm.location_dest_id != sm.location_final_id
            AND sr.action IN ('pull', 'pull_push')
        """,
    )


def fill_stock_putaway_rule_sublocation(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_putaway_rule
        SET sublocation = 'closest_location'
        WHERE storage_category_id is not null""",
    )


@openupgrade.migrate()
def migrate(env, version=None):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.add_columns(env, _new_columns)
    fill_product_template_is_storable(env)
    fill_stock_move_location_dest_id(env)
    fill_stock_putaway_rule_sublocation(env)
