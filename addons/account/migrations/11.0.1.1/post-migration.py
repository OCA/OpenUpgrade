# © 2017 bloopark systems (<http://bloopark.de>)
# © 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def migrate_account_tax_cash_basis(env):
    # Migrate tax exigibility settings
    if not openupgrade.column_exists(
            env.cr, 'account_tax',
            openupgrade.get_legacy_name('use_cash_basis')):
        return  # pragma: no cover
    field = AsIs(openupgrade.get_legacy_name('use_cash_basis'))
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_tax
        SET tax_exigibility = 'on_payment'
        WHERE %s IS TRUE;""", (field,))
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_tax
        SET tax_exigibility = 'on_invoice'
        WHERE %s IS NOT TRUE;""", (field,))
    openupgrade.logged_query(
        env.cr,
        """UPDATE res_company rc
        SET tax_exigibility = TRUE WHERE EXISTS (
            SELECT id FROM account_tax
            WHERE company_id = rc.id AND tax_exigibility = 'on_payment')""")


@openupgrade.migrate()
def migrate(env, version):
    # map old / non existing value 'proforma' and 'proforma2' to value 'draft'
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('state'), 'state',
        [('proforma', 'draft'), ('proforma2', 'draft')],
        table='account_invoice', write='sql')
    # copy statement_line_id values from account.move to account.move.line
    env.cr.execute("""
        UPDATE account_move_line aml
        SET statement_line_id = am.statement_line_id
        FROM account_move am
        WHERE aml.move_id = am.id AND am.statement_line_id IS NOT NULL;
    """)
    # Migrate draft payments to cancelled if they don't have any move lines
    # but they have been posted before (i.e. when move_name is set)
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_payment
        SET state = 'cancelled'
        WHERE state = 'draft' AND move_name IS NOT NULL
        AND id NOT IN (
            SELECT payment_id FROM account_move_line
            WHERE payment_id IS NOT NULL)""")
    # Populate new 'sequence' field according to previous order field 'name'
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_payment_term apt
        SET sequence = sub.sequence
        FROM (SELECT id, row_number() over (ORDER BY name asc) AS sequence
              FROM account_payment_term) sub
        WHERE sub.id = apt.id """)

    migrate_account_tax_cash_basis(env)

    openupgrade.load_data(
        env.cr, 'account', 'migrations/11.0.1.1/noupdate_changes.xml',
    )
