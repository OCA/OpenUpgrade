# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.logging()
def fill_account_invoice_line_total_tax_python(env):
    """Compute via regular way invoice lines with python computed taxes."""
    lines = env['account.invoice.line'].search([])
    for line in lines:
        types = ['percent', 'fixed', 'group', 'division', 'code']
        taxes = line.invoice_line_tax_ids
        if (not any(x.amount_type == 'code' for x in taxes) or
                any(x.amount_type not in types for x in taxes)):
            continue
        # This has been extracted from `_compute_price` method
        currency = line.invoice_id and line.invoice_id.currency_id or None
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        # This is enclosed in a try for avoiding errors due to outdated code
        # not being valid in new version. In such case, price_total will be 0
        try:
            taxes = line.invoice_line_tax_ids.compute_all(
                price, currency, line.quantity, product=line.product_id,
                partner=line.invoice_id.partner_id,
            )
            line.price_total = taxes['total_included']
        except Exception:
            pass


@openupgrade.migrate()
def migrate(env, version):
    fill_account_invoice_line_total_tax_python(env)
