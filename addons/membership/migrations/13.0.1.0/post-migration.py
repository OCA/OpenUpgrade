# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_invoice_line_relation(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE membership_membership_line mml
        SET account_invoice_line = aml.id
        FROM account_invoice_line ail
        JOIN account_move_line aml ON aml.old_invoice_line_id = ail.id
        WHERE mml.account_invoice_line = ail.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    update_invoice_line_relation(env)
