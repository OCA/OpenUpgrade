# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_renamed_models = [
    ("stock.valuation.layer", "product.value"),
]

_renamed_tables = [
    ("stock_valuation_layer", "product_value"),
]

_renamed_fields = [
    ("product.value", "product_value", "", ""),
]

_copied_columns = {
    "product_value": [
        ("create_date", "date", None),
        ("create_uid", "user_id", None),
        ("stock_move_id", "move_id", None),
    ],
}

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
    openupgrade.rename_models(env.cr, _renamed_models)
    openupgrade.rename_tables(env.cr, _renamed_tables)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.copy_columns(env.cr, _copied_columns)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
    stock_lot_avg_cost(env)
    stock_move_is_fields(env)
