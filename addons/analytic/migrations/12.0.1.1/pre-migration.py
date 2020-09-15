# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copies = {
    'account_analytic_line': [
        ('company_id', None, None),
    ],
}


def migrate_account_analytic_distribution_pre(cr):
    """Prepare data for migrating OCA module."""
    # Check if the module was installed in previous version checking the
    # existence of one of its tables
    if openupgrade.table_exists(cr, 'account_analytic_distribution'):
        openupgrade.rename_tables(
            cr, [('account_analytic_distribution', None)],
        )

def fill_analytic_line_empty_names(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_analytic_line
        SET name = '(No description)'
        WHERE name IS NULL
        """,
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    migrate_account_analytic_distribution_pre(cr)
    fill_analytic_line_empty_names(cr)
