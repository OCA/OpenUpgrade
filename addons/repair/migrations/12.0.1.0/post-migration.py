# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_repair_line_price_subtotal(env):
    lines = env['repair.line'].search([])
    for line in lines:
        line._compute_price_subtotal()


def fill_repair_fee_price_subtotal(env):
    fees = env['repair.fee'].search([])
    for fee in fees:
        fee._compute_price_subtotal()


@openupgrade.migrate()
def migrate(env, version):
    fill_repair_line_price_subtotal(env)
    fill_repair_fee_price_subtotal(env)
    openupgrade.load_data(
        env.cr, 'repair', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'repair', [
            'mail_template_repair_quotation',
        ],
    )
