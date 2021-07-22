# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    "product_product_sale_coupon_reward_rel": [
        ("sale_coupon_reward_id", "coupon_reward_id"),
    ],
    "sale_coupon_program_sale_order_rel": [
        ("sale_coupon_program_id", "coupon_program_id"),
    ],
}

_model_renames = [
    ("sale.coupon", "coupon.coupon"),
    ("sale.coupon.generate", "coupon.generate.wizard"),
    ("sale.coupon.program", "coupon.program"),
    ("sale.coupon.reward", "coupon.reward"),
    ("sale.coupon.rule", "coupon.rule"),
    ("report.sale_coupon.report_coupon", "report.coupon.report_coupon"),
]

_table_renames = [
    ("sale_coupon", "coupon_coupon"),
    ("sale_coupon_generate", "coupon_generate_wizard"),
    ("sale_coupon_program", "coupon_program"),
    ("sale_coupon_reward", "coupon_reward"),
    ("sale_coupon_rule", "coupon_rule"),
    ("product_product_sale_coupon_reward_rel", "coupon_reward_product_product_rel"),
    ("sale_coupon_program_sale_order_rel", "coupon_program_sale_order_rel"),
]

_xmlid_renames = [
    # rename suffix:
    ("coupon.sale_coupon_action", "coupon.coupon_action"),
    ("coupon.sale_coupon_generate_action", "coupon.coupon_generate_action"),
    (
        "coupon.sale_coupon_program_action_coupon_program",
        "coupon.coupon_program_action_coupon_program",
    ),
    (
        "coupon.sale_coupon_program_action_promo_program",
        "coupon.coupon_program_action_promo_program",
    ),
    ("coupon.sale_coupon_generate_view_form", "coupon.coupon_generate_view_form"),
    (
        "coupon.sale_coupon_program_view_form_common",
        "coupon.coupon_program_view_form_common",
    ),
    ("coupon.sale_coupon_view_form", "coupon.coupon_view_form"),
    ("coupon.sale_coupon_view_tree", "coupon.coupon_view_tree"),
    (
        "coupon.sale_coupon_program_view_promo_program_search",
        "coupon.coupon_program_view_promo_program_search",
    ),
    (
        "coupon.sale_coupon_program_view_promo_program_tree",
        "coupon.coupon_program_view_promo_program_tree",
    ),
    (
        "coupon.sale_coupon_program_view_form",
        "coupon.coupon_program_view_coupon_program_form",
    ),
    ("coupon.sale_coupon_program_view_search", "coupon.coupon_program_view_search"),
    ("coupon.sale_coupon_program_view_tree", "coupon.coupon_program_view_tree"),
    ("coupon.view_sale_coupon_program_kanban", "coupon.view_coupon_program_kanban"),
    (
        "coupon.sale_coupon_program_view_promo_program_form",
        "coupon.coupon_program_view_promo_program_form",
    ),
    # rename prefix:
    (
        "coupon.sale_coupon_apply_code_action",
        "sale_coupon.sale_coupon_apply_code_action",
    ),
    ("coupon.sale_order_action", "sale_coupon.sale_order_action"),
    ("coupon.access_applicability_manager", "sale_coupon.access_applicability_manager"),
    (
        "coupon.access_applicability_salesman",
        "sale_coupon.access_applicability_salesman",
    ),
    ("coupon.access_coupon_manager", "sale_coupon.access_coupon_manager"),
    ("coupon.access_coupon_salesman", "sale_coupon.access_coupon_salesman"),
    ("coupon.access_program_manager", "sale_coupon.access_program_manager"),
    ("coupon.access_program_salesman", "sale_coupon.access_program_salesman"),
    ("coupon.access_reward_manager", "sale_coupon.access_reward_manager"),
    ("coupon.access_reward_salesman", "sale_coupon.access_reward_salesman"),
    ("coupon.menu_coupon_type_config", "sale_coupon.menu_coupon_type_config"),
    ("coupon.menu_promotion_type_config", "sale_coupon.menu_promotion_type_config"),
    (
        "coupon.res_config_settings_view_form",
        "sale_coupon.res_config_settings_view_form",
    ),
    (
        "coupon.sale_coupon_apply_code_view_form",
        "sale_coupon.sale_coupon_apply_code_view_form",
    ),
    ("coupon.sale_order_view_form", "sale_coupon.sale_order_view_form"),
]


def install_new_modules(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state='to install'
        WHERE name = 'sale_coupon' AND state='uninstalled'""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    install_new_modules(env)
