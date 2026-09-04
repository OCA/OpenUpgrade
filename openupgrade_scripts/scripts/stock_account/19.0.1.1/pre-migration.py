# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_deleted_xmlids = [
    "stock_account.stock_valuation_layer_company_rule",
    "stock_account.group_stock_accounting_automatic",
]


def stock_lot_avg_cost(env):
    """
    Precreate stock.lot#avg_cost to avoid compute method
    """
    openupgrade.add_fields(
        env,
        [
            ("avg_cost", "stock.lot", "stock_lot", "float", None, "stock_account", 0),
        ],
    )


def stock_move_is_fields(env):
    """
    Precreate stock.move#is_* to avoid compute method
    """
    openupgrade.add_fields(
        env,
        [
            (
                "is_in",
                "stock.move",
                "stock_move",
                "boolean",
                None,
                "stock_account",
                False,
            ),
            (
                "is_out",
                "stock.move",
                "stock_move",
                "boolean",
                None,
                "stock_account",
                False,
            ),
            (
                "is_dropship",
                "stock.move",
                "stock_move",
                "boolean",
                None,
                "stock_account",
                False,
            ),
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
    stock_lot_avg_cost(env)
    stock_move_is_fields(env)
