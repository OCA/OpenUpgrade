# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_renamed_models = [
    ("procurement.group", "stock.reference"),
    ("stock.package_level", "stock.package.history"),
    ("stock.quant.package", "stock.package"),
]

_renamed_tables = [
    ("procurement_group", "stock_reference"),
    ("stock_package_level", "stock_package_history"),
    ("stock_quant_package", "stock_package"),
]

_renamed_fields = [
    ("stock.reference", "stock_reference", "stock_move_ids", "move_ids"),
    ("stock.move.line", "stock_move_line", "package_level_id", "package_history_id"),
    ("stock.picking", "stock_picking", "package_level_ids", "package_history_ids"),
    ("stock.route", "stock_route", "packaging_selectable", "package_type_selectable"),
]

_renamed_xmlids = [
    ("stock.seq_quant_package", "stock.seq_package"),
]

_deleted_xmlids = [
    "stock.stock_quant_package_comp_rule",
    "stock.sequence_proc_group",
    "stock.constraint_stock_warehouse_orderpoint_qty_multiple_check",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _renamed_models)
    openupgrade.rename_tables(env.cr, _renamed_tables)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
