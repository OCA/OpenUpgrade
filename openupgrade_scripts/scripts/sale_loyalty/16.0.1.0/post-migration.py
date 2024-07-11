# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_deleted_xml_records = [
    "sale_loyalty.sale_coupon_apply_code_rule",
]


def convert_applied_coupons_from_sale_order_to_many2many(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO loyalty_card_sale_order_rel (sale_order_id, loyalty_card_id)
        SELECT sales_order_id, id
        FROM loyalty_card
        WHERE sales_order_id IS NOT NULL
        """,
    )


def fill_code_enabled_rule_ids_from_sale_order(env):
    """This field relates the id of a rule to the id of
    a sales order to which it has been applied, provided that the rule belongs to an
    applicable promotion with code."""
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO loyalty_rule_sale_order_rel (sale_order_id, loyalty_rule_id)
        SELECT lc.order_id, lr.id
        FROM loyalty_card lc
        JOIN loyalty_rule lr ON lc.program_id = lr.program_id
        JOIN loyalty_program lp ON lr.program_id = lp.id
        WHERE lr.mode = 'with_code'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "sale_loyalty", "16.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    convert_applied_coupons_from_sale_order_to_many2many(env)
    fill_code_enabled_rule_ids_from_sale_order(env)
