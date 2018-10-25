# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_account_analytic_line_company_id(cr):
    cr.execute(
        """
        UPDATE account_analytic_line aal
        SET company_id = aaa.%s 
        FROM account_analytic_account aaa
        WHERE aal.account_id = aaa.id AND aaa.%s IS NOT NULL
        """, (
            AsIs(openupgrade.get_legacy_name('company_id')),
            AsIs(openupgrade.get_legacy_name('company_id')),
        ),
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_account_analytic_line_company_id(cr)
