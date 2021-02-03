# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql


def update_account_move_team_partner_ids(cr):
    openupgrade.logged_query(
        cr, """
            UPDATE account_move am
            SET partner_shipping_id = ai.partner_shipping_id,
            team_id = ai.team_id,
            narration = ai.comment
            FROM account_invoice ai
            WHERE am.old_invoice_id = ai.id
            """
    )


def update_account_move_utm_fields(cr):
    if not openupgrade.column_exists(cr, "account_invoice", "campaign_id"):
        return
    openupgrade.logged_query(
        cr,
        """UPDATE account_move am
        SET campaign_id = ai.campaign_id,
            medium_id = ai.medium_id,
            source_id = ai.source_id
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id"""
    )


def update_sale_order_line_invoice_rel(cr):
    openupgrade.logged_query(
        cr, sql.SQL(
            """INSERT INTO sale_order_line_invoice_rel
            (invoice_line_id, order_line_id)
            SELECT aml.id, order_line_id
            FROM account_invoice_line ail
            JOIN account_move_line aml ON aml.old_invoice_line_id = ail.id
            JOIN {} rel ON rel.invoice_line_id = ail.id"""
        ).format(sql.Identifier("ou_sale_order_line_invoice_rel"))
    )


def update_product_attribute_custom_value(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE product_attribute_custom_value pacv
        SET custom_product_template_attribute_value_id = ptav.id
        FROM product_attribute_value pav,
            sale_order_line sol,
            product_product pp,
            product_template_attribute_value ptav
        WHERE pacv.{} = pav.id
            AND pacv.custom_product_template_attribute_value_id IS NULL
            AND sol.id = pacv.sale_order_line_id
            AND pp.id = sol.product_id
            AND ptav.product_attribute_value_id = pav.id
            AND ptav.product_tmpl_id = pp.product_tmpl_id
        """.format(openupgrade.get_legacy_name('attribute_value_id'))
    )


def check_optional_products(env):
    """Don't lose this feature if used."""
    env.cr.execute("SELECT COUNT(*) FROM product_optional_rel")
    if env.cr.fetchone()[0] > 0:
        module = env["ir.module.module"].search(
            [("name", "=", "sale_product_configurator")]
        )
        if module.state == "uninstalled":
            module.write({"state": "to install"})
        openupgrade.update_module_moved_fields(
            env.cr, "product.product", ["optional_product_ids"], "sale", "sale_product_configurator"
        )
        openupgrade.update_module_moved_fields(
            env.cr, "product.template", ["optional_product_ids"], "sale", "sale_product_configurator"
        )


def fill_order_signed_date(env):
    """Put the confirmation date as signature date as most nearer when the
    order has been signed.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE sale_order
        SET signed_on = confirmation_date
        WHERE signed_by IS NOT NULL""",
    )


def fill_confirmation_date(env):
    """On v13, there's no different field for order date and confirmation date.
    It's overwritten when confirming the sales order. We need then to copy
    the v12 confirmation date over order date for confirmed orders.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE sale_order
        SET date_order = confirmation_date
        WHERE state IN ('sale', 'done')
        AND confirmation_date IS NOT NULL"""
    )


def check_sale_auto_done(env):
    """System parameter has been replaced by a security group, so we need to
    add such group if the system parameter was present.
    """
    if env["ir.config_parameter"].sudo().get_param("sale.auto_done_setting"):
        env.ref("base.group_user").implied_ids = [
            (4, env.ref("sale.group_auto_done_setting").id),
        ]


@openupgrade.migrate()
def migrate(env, version):
    update_account_move_team_partner_ids(env.cr)
    update_account_move_utm_fields(env.cr)
    update_sale_order_line_invoice_rel(env.cr)
    update_product_attribute_custom_value(env.cr)
    check_optional_products(env)
    fill_order_signed_date(env)
    fill_confirmation_date(env)
    check_sale_auto_done(env)
    openupgrade.load_data(env.cr, 'sale', 'migrations/13.0.1.1/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'sale', [
            'email_template_edi_sale',
        ],
    )
