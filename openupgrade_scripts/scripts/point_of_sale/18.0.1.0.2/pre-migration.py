# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def set_pos_printer_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_printer pp
        SET company_id = COALESCE(pp.company_id, pc.company_id)
        FROM pos_config pc
        JOIN pos_config_printer_rel rel ON rel.config_id = pc.id
        WHERE rel.printer_id = pp.id AND pc.active
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_printer pp
        SET company_id = COALESCE(pp.company_id, pc.company_id)
        FROM pos_config pc
        JOIN pos_config_printer_rel rel ON rel.config_id = pc.id
        WHERE rel.printer_id = pp.id AND pc.active IS DISTINCT FROM TRUE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE pos_printer pp
        SET company_id = {env.company.id}
        WHERE pp.company_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            ("pos.category", "pos_category", "child_id", "child_ids"),
            ("pos.order", "pos_order", "note", "floating_order_name"),
            (
                "pos.config",
                "pos_config",
                "iface_customer_facing_display_background_image_1920",
                "customer_display_bg_img_name",
            ),
        ],
    )
    if openupgrade.column_exists(env.cr, "product_template", "description_self_order"):
        # from pos_self_order
        openupgrade.rename_fields(
            env,
            [
                (
                    "product.template",
                    "product_template",
                    "description_self_order",
                    "public_description",
                ),
            ],
        )
    openupgrade.add_columns(
        env,
        [
            ("pos.order", "amount_difference", "float", None, "pos_order"),
            ("pos.order.line", "price_type", "selection", "original", "pos_order_line"),
            ("pos.printer", "company_id", "many2one", None, "pos_printer"),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_order
        SET amount_difference = amount_paid - amount_total
        """,
    )
    set_pos_printer_company_id(env)
