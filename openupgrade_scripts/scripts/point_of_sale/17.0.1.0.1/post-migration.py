# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_account_move_pos_refunded_invoice_ids(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO refunded_invoices (refund_account_move, original_account_move)
        SELECT am.id as refund_account_move, am2.id as original_account_move
        FROM account_move am
        JOIN pos_order pos ON pos.account_move = am.id
        JOIN pos_order_line pol ON pol.order_id = pos.id
        JOIN pos_order_line pol2 ON pol.refunded_orderline_id = pol2.id
        JOIN pos_order pos2 ON pol2.order_id = pos2.id
        JOIN account_move am2 ON pos2.account_move = am2.id
        GROUP BY am.id, am2.id""",
    )


def fill_pos_order_shipping_date(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_order pos
        SET shipping_date = date_order
        WHERE to_ship
        """,
    )


def fill_limited_product_count(env):
    """In v16, you could use the limited_partners_loading and limited_products_amount
    fields in pos.config to specify whether to perform a limited load and, if so,
    the number of products to load; it is important to maintain this behavior in v17.
    """
    env.cr.execute(
        """
        SELECT CASE
            WHEN EXISTS (
                SELECT 1
                FROM pos_config
                WHERE limited_partners_loading
            )
            THEN COALESCE(
                MIN(limited_products_amount) FILTER (
                    WHERE limited_partners_loading
                      AND limited_products_amount > 0
                ),
                0
            )
            ELSE 0
        END
        FROM pos_config
        """
    )
    limited_product_count = env.cr.fetchone()[0]
    env["ir.config_parameter"].set_param(
        "point_of_sale.limited_product_count", str(limited_product_count)
    )


def product_template_convert_pos_categ_id_m2o_to_m2m(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["product.template"],
        "product_template",
        "pos_categ_ids",
        "pos_categ_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_account_move_pos_refunded_invoice_ids(env)
    fill_pos_order_shipping_date(env)
    fill_limited_product_count(env)
    product_template_convert_pos_categ_id_m2o_to_m2m(env)
    openupgrade.load_data(env, "point_of_sale", "17.0.1.0.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "point_of_sale.rule_pos_account_move_line",
            "point_of_sale.rule_pos_account_move",
        ],
    )
