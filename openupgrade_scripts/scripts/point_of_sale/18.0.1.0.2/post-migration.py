# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from uuid import uuid4

from openupgradelib import openupgrade


def fill_pos_config_token(env):
    """Set the access_token to an appropriate value, thereby preventing all records
    from having the same value and causing unexpected consequences.
    """
    for config in env["pos.config"].search([]):
        config.access_token = uuid4().hex[:16]


def fill_pos_order_reversed_pos_order_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am2
        SET reversed_pos_order_id = po.id
        FROM pos_order po
        JOIN pos_session ps ON po.session_id = ps.id AND ps.state = 'closed'
        JOIN pos_config pc ON ps.config_id = pc.id
        JOIN account_journal aj ON pc.journal_id = aj.id
        JOIN account_move am ON po.account_move = am.id
            AND am.state = 'posted' AND am.journal_id = pc.invoice_journal_id
            AND am.invoice_origin = po.name
        JOIN account_move session_move ON session_move.id = ps.move_id
        WHERE po.partner_id IS NOT NULL AND
            am2.journal_id = pc.journal_id
            -- we find correct move by looking into the ref
            AND am2.ref like CONCAT('%', session_move.name, '%')
            AND am2.ref like CONCAT('% ', po.name, '%')
            AND am2.ref like CONCAT('%', ps.name, '%')""",
    )


def fill_pos_config_customer_display_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_config pc
        SET customer_display_type = CASE
            WHEN pc.iface_customer_facing_display_via_proxy THEN 'proxy'
            WHEN pc.iface_customer_facing_display_local THEN 'local'
            ELSE 'none' END""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_config pc
        SET customer_display_bg_img_name = CASE
            WHEN pc.customer_display_type != 'none' THEN 'image_display_' || pc.id
            ELSE NULL END""",
    )


def update_pos_config_show_images(env):
    show_product_images = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("point_of_sale.show_product_images", "yes")
    )
    if show_product_images == "no":
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE pos_config pc
            SET show_product_images = FALSE
            """,
        )
    show_category_images = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("point_of_sale.show_category_images", "yes")
    )
    if show_category_images == "no":
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE pos_config pc
            SET show_category_images = FALSE
            """,
        )


def fill_pos_uuid(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_order
        SET uuid = gen_random_uuid()
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_payment
        SET uuid = gen_random_uuid()
        """,
    )


def update_res_company_point_of_sale_ticket_portal_url_display_mode(env):
    # in v17, url was always shown
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company rc
        SET point_of_sale_ticket_portal_url_display_mode = CASE
            WHEN rc.point_of_sale_use_ticket_qr_code THEN 'qr_code_and_url'
            ELSE 'url' END""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_pos_order_reversed_pos_order_id(env)
    fill_pos_config_customer_display_type(env)
    fill_pos_config_token(env)
    fill_pos_uuid(env)
    update_pos_config_show_images(env)
    update_res_company_point_of_sale_ticket_portal_url_display_mode(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "point_of_sale.0_01",
            "point_of_sale.0_02",
        ],
    )
    imd = env["ir.model.data"].search(
        [("module", "=", "point_of_sale"), ("name", "=", "pos_config_main")], limit=1
    )
    if imd:
        imd.unlink()
    imd = env["ir.model.data"].search(
        [("module", "=", "point_of_sale"), ("name", "=", "product_product_consumable")],
        limit=1,
    )
    if imd and not openupgrade.column_exists(
        env.cr, "pos_config", "discount_product_id"
    ):
        # pos_discount is not installed
        imd.unlink()
    else:
        openupgrade.rename_xmlids(
            env.cr,
            [
                (
                    "point_of_sale.product_product_consumable",
                    "pos_discount.product_product_consumable",
                )
            ],
        )
