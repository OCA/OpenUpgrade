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


def merge_sale_gift_card_to_sale_loyalty_card(env):
    # Update the coupon_id column in the sale_order_line table with the ID of the
    # loyalty_card table based on certain criteria and relationships established between
    # the loyalty_card, loyalty_reward and gift_card tables
    # program_id is added to the gift_card table in the loyalty migration script.
    if not openupgrade.table_exists(env.cr, "gift_card"):
        return
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line AS sol
        SET coupon_id = lc.id
        FROM loyalty_card AS lc
        JOIN loyalty_reward AS lr ON lc.program_id = lr.program_id
        JOIN gift_card AS gc ON lc.program_id = gc.program_id
        WHERE sol.reward_id = lr.id
        AND lr.program_id = lc.program_id
        AND lc.program_id = gc.program_id
        AND sol.gift_card_id = gc.id
        AND sol.reward_id IS NOT NULL
        """,
    )
    # Values corresponding to the order_id and coupon_id columns of the sale_order_line
    # table where reward_id is not null and gift_card_id is not null
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO loyalty_card_sale_order_rel (sale_order_id, loyalty_card_id)
        SELECT sol.order_id, sol.coupon_id
        FROM sale_order_line AS sol
        WHERE sol.reward_id IS NOT NULL
        AND sol.gift_card_id IS NOT NULL
        """,
    )


def _generate_sale_order_coupon_points(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO sale_order_coupon_points (
            coupon_id, order_id, points, create_uid, write_uid, create_date, write_date
        )
        SELECT
            lc.id AS coupon_id,
            lc.order_id,
            lc.points,
            lc.create_uid,
            lc.write_uid,
            lc.create_date,
            lc.write_date
        FROM loyalty_card lc
        LEFT JOIN sale_order_coupon_points socp
        ON lc.order_id = socp.order_id
        AND lc.id = socp.coupon_id
        WHERE lc.order_id IS NOT NULL
        AND socp.id IS NULL
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
    merge_sale_gift_card_to_sale_loyalty_card(env)
    _generate_sale_order_coupon_points(env)
