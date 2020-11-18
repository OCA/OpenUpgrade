# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import sql
from openupgradelib import openupgrade


def update_invoice_line_relation(env):
    column = "account_invoice_line"
    openupgrade.rename_columns(
        env.cr, {"membership_membership_line": [(column, None)]}
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL("ALTER TABLE membership_membership_line ADD {} INT4").format(
            sql.Identifier(column)
        )
    )
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE membership_membership_line mml
            SET account_invoice_line = aml.id
            FROM account_invoice_line ail
            JOIN account_move_line aml ON aml.old_invoice_line_id = ail.id
            WHERE mml.{} = ail.id"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name(column))
        ),
    )


@openupgrade.migrate()
def migrate(env, version):
    update_invoice_line_relation(env)
