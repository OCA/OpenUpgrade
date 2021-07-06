# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    "stock_move": [
        ("priority", None, None),
    ],
    "stock_picking": [
        ("priority", None, None),
    ],
}

_field_renames = [("stock.move", "stock_move", "date_expected", "date_deadline")]

_xmlid_renames = [
    ("stock.action_orderpoint_form", "stock.action_orderpoint"),
    ("stock.access_stock_picking_portal", "sale_stock.access_stock_picking_portal"),
]


def fast_precreate_orderpoint_product_category_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_warehouse_orderpoint
        ADD COLUMN product_category_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_warehouse_orderpoint swo
        SET product_category_id = pt.categ_id
        FROM product_product pp
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE swo.product_id = pp.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fast_precreate_orderpoint_product_category_id(env)
    # Disappeared constraint
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE stock_production_lot
           DROP CONSTRAINT IF EXISTS stock_production_lot_name_ref_uniq""",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["stock.constraint_stock_production_lot_name_ref_uniq"]
    )
