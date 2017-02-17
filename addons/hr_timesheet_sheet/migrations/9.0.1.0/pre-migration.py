# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def prepopulate_fields(cr):

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_analytic_line' AND
    column_name='sheet_id'""")

    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_analytic_line ADD COLUMN sheet_id
            integer;
            COMMENT ON COLUMN account_analytic_line.sheet_id IS
            'Sheet';
            """)

    cr.execute("""
        UPDATE account_analytic_line aal
        SET sheet_id = hat.sheet_id
        FROM hr_analytic_timesheet hat
        WHERE hat.line_id = aal.id
    """)


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute("""
    DROP VIEW IF EXISTS hr_timesheet_sheet_sheet_account;
    """)
    prepopulate_fields(cr)
