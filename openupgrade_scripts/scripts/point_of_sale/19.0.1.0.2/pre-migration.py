# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

renamed_fields = [
    ("pos.config", "pos_config", "sequence_id", "order_seq_id"),
    ("pos.config", "pos_config", "sequence_line_id", "order_line_seq_id"),
    ("pos.order", "pos_order", "general_note", "general_customer_note"),
]


renamed_field_references = [
    ("pos.order", "procurement_group_id", "stock_reference_ids"),
    ("stock.reference", "pos_order_id", "pos_order_ids"),
]


renamed_xmlids = [
    (
        "point_of_sale.constraint_pos_order_line_uuid_unique",
        "point_of_sale.constraint_pos_order_line_unique_uuid",
    ),
    (
        "point_of_sale.constraint_pos_order_uuid_unique",
        "point_of_sale.constraint_pos_order_unique_uuid",
    ),
    (
        "point_of_sale.constraint_pos_payment_uuid_unique",
        "point_of_sale.constraint_pos_payment_unique_uuid",
    ),
]


deleted_xmlids = [
    "point_of_sale.product_attribute_custom_value_pos_rule",
    "point_of_sale.pos_email_marketing_template",
    "point_of_sale.product_category_pos",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
    openupgrade.rename_field_references(env, renamed_field_references)
    openupgrade.rename_xmlids(env.cr, renamed_xmlids)
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
