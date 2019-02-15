# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


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


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_account_analytic_line_company_id(cr)
    fill_account_analytic_line_currency_id(cr)
