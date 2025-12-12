# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Holger Brunn
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _sale_order_populate_locked_field(env):
    """Set state of sale orders in state 'done' to 'sale' and lock them."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
        SET locked = True, state = 'sale'
        WHERE state = 'done'
        """,
    )
    # Update by SQL the corresponding related state field in sale.order.line
    openupgrade.logged_query(
        env.cr, "UPDATE sale_order_line SET state = 'sale' WHERE state = 'done'"
    )


def _fill_res_company_deposit_default_product_id(env):
    product_id = env["ir.config_parameter"].get_param("sale.default_deposit_product_id")
    if product_id:
        companies = env["res.company"].search([])
        companies.write({"sale_down_payment_product_id": int(product_id)})


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "sale", "17.0.1.2/noupdate_changes.xml")
    _sale_order_populate_locked_field(env)
    _fill_res_company_deposit_default_product_id(env)
