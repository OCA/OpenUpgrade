from openupgradelib import openupgrade

from odoo.tools.translate import _


def _create_column_for_avoiding_automatic_computing(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_move ADD COLUMN IF NOT EXISTS reservation_date date;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_location ADD COLUMN IF NOT EXISTS next_inventory_date date;
        """,
    )


def _fill_stock_quant_package_name_if_null(env):
    non_sequenced_name = _("Unknown Pack")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE stock_quant_package
        SET name = '{non_sequenced_name}'
        WHERE name IS NULL;
        """,
    )


def _fill_stock_quant_in_date(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_quant
        SET in_date = create_date
        WHERE in_date IS NULL;
        """,
    )


def remove_table_constrains(env):
    openupgrade.remove_tables_fks(
        env.cr,
        [
            "stock_inventory",
            "stock_inventory_line",
            "stock_inventory_stock_location_rel",
            "product_product_stock_inventory_rel",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr, "stock_location", "comment", "comment", verbose=False
    )
    openupgrade.convert_field_to_html(
        env.cr, "stock_picking", "note", "note", verbose=False
    )
    openupgrade.add_fields(
        env,
        [
            (
                "inventory_quantity_set",
                "stock.quant",
                "stock_quant",
                "boolean",
                False,
                "stock",
                False,
            ),
            (
                "inventory_diff_quantity",
                "stock.quant",
                "stock_quant",
                "float",
                False,
                "stock",
                0,
            ),
        ],
    )
    _create_column_for_avoiding_automatic_computing(env)
    _fill_stock_quant_package_name_if_null(env)
    _fill_stock_quant_in_date(env)
    remove_table_constrains(env)
