# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import sql
from openupgradelib import openupgrade


def update_repair_fee_invoice_relation(env):
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE repair_fee rf
            SET invoice_line_id = aml.id
            FROM account_move_line aml
            WHERE rf.{} = aml.old_invoice_line_id"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("invoice_line_id"))
        ),
    )


def update_repair_line_invoice_relation(env):
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE repair_line rl
            SET invoice_line_id = aml.id
            FROM account_move_line aml
            WHERE rl.{} = aml.old_invoice_line_id"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("invoice_line_id"))
        ),
    )


def update_repair_order_invoice_relation(env):
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE repair_order ro
            SET invoice_id = am.id
            FROM account_move am
            WHERE ro.{} = am.old_invoice_id"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("invoice_id"))
        ),
    )


def update_repair_order_user_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE repair_order
        SET user_id = create_uid""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "repair",
        "migrations/13.0.1.0/noupdate_changes.xml"
    )
    update_repair_fee_invoice_relation(env)
    update_repair_line_invoice_relation(env)
    update_repair_order_invoice_relation(env)
    update_repair_order_user_id(env)
