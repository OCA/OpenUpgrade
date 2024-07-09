# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo.tools.translate import _

_deleted_xml_records = [
    "loyalty.sale_coupon_generate_rule",
]


def convert_loyalty_program_rewards(env):
    openupgrade.m2o_to_x2m(
        env.cr, env["loyalty.program"], "loyalty_program", "reward_ids", "reward_id"
    )


def convert_loyalty_program_rules(env):
    openupgrade.m2o_to_x2m(
        env.cr, env["loyalty.program"], "loyalty_program", "rule_ids", "rule_id"
    )


def compute_portal_point_name(env):
    """This is a computed field, but the _program_type_default_values method of the
    loyalty module sets the following values in portal_point_name depending on the
    program_type field. This is done in post so that the language context can be used."""
    portal_point_names = {
        "coupons": _("Coupon point(s)"),
        "promotion": _("Promo point(s)"),
        "gift_card": _("Gift Card"),
        "loyalty": _("Loyalty point(s)"),
        "ewallet": _("eWallet"),
        "promo_code": _("Discount point(s)"),
        "buy_x_get_y": _("Credit(s)"),
        "next_order_coupons": _("Coupon point(s)"),
    }
    loyalty_programs = env["loyalty.program"].search([])
    for program in loyalty_programs:
        if program.program_type in portal_point_names:
            translated_name = portal_point_names[program.program_type]
            # By default when the module is installed it contains the terms in the
            # language code "en_US".
            program.with_context(lang="en_US").write(
                {"portal_point_name": translated_name}
            )


@openupgrade.migrate()
def migrate(env, version):
    convert_loyalty_program_rewards(env)
    convert_loyalty_program_rules(env)
    compute_portal_point_name(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
