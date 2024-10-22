# Copyright 2024 Le Filament
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _compute_repair_price_total(env, model):
    fees = env[model].search([])
    fees._compute_price_total_and_subtotal()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "repair", "16.0.1.0/noupdate_changes.xml")
    _compute_repair_price_total(env, "repair.fee")
    _compute_repair_price_total(env, "repair.line")
