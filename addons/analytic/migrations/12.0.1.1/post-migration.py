# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import sql


def fill_account_analytic_line_company_id(cr):
    openupgrade.logged_query(
        cr, """UPDATE account_analytic_line aal
        SET company_id = aaa.company_id
        FROM account_analytic_account aaa
        WHERE aal.account_id = aaa.id
        """,
    )


def fill_account_analytic_line_currency_id(cr):
    openupgrade.logged_query(
        cr, """UPDATE account_analytic_line aal
        SET currency_id = rc.currency_id
        FROM res_company rc
        WHERE aal.company_id = rc.id
        """,
    )


def migrate_account_analytic_distribution_post(cr):
    """Move needed data for equivalent OCA module features."""
    table = openupgrade.get_legacy_name('account_analytic_distribution')
    if not openupgrade.table_exists(cr, table):
        return
    column = openupgrade.get_legacy_name('analytic_distribution_id')
    cr.execute(sql.SQL(
        "ALTER TABLE account_analytic_tag ADD {column} int4"
    ).format(column=sql.Identifier(column)))
    # Analytic distribution > Analytic tag
    openupgrade.logged_query(
        cr, sql.SQL("""
        INSERT INTO account_analytic_tag
        (name, company_id, {column},
         create_date, create_uid, write_date, write_uid)
        SELECT name, company_id, id,
            create_date, create_uid, write_date, write_uid
        FROM {table}
        """).format(
            table=sql.Identifier(table),
            column=sql.Identifier(column),
        )
    )
    # Analytic distribution rule > "New" analytic distribution
    openupgrade.logged_query(
        cr, sql.SQL("""
        INSERT INTO account_analytic_distribution
        (account_id, percentage, tag_id,
         create_date, create_uid, write_date, write_uid)
        SELECT aadr.analytic_account_id, aadr.percent, aat.id,
            aadr.create_date, aadr.create_uid, aadr.write_date, aadr.write_uid
        FROM account_analytic_distribution_rule aadr
        JOIN account_analytic_tag aat
            ON aat.{column} = aadr.distribution_id
        """).format(
            column=sql.Identifier(column),
        ),
    )
    # Distribution in invoice line > Tag in invoice line
    openupgrade.logged_query(
        cr, sql.SQL("""
        INSERT INTO account_analytic_tag_account_invoice_line_rel
        (account_analytic_tag_id, account_invoice_line_id)
        SELECT aat.id, ail.id
        FROM account_invoice_line ail
        JOIN account_analytic_tag aat
            ON aat.{column} = ail.analytic_distribution_id
        """).format(
            column=sql.Identifier(column),
        ),
    )
    # Distribution in move line > Tag in move line
    openupgrade.logged_query(
        cr, sql.SQL("""
        INSERT INTO account_analytic_tag_account_move_line_rel
        (account_analytic_tag_id, account_move_line_id)
        SELECT aat.id, aml.id
        FROM account_move_line aml
        JOIN account_analytic_tag aat
            ON aat.{column} = aml.analytic_distribution_id
        """).format(
            column=sql.Identifier(column),
        ),
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_account_analytic_line_company_id(cr)
    fill_account_analytic_line_currency_id(cr)
    migrate_account_analytic_distribution_post(cr)
