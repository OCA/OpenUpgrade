# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(cr, version):
    cr.execute("""
    DROP VIEW IF EXISTS hr_timesheet_sheet_sheet_account;
    """)
    # Inherited Views that encountered errors while running the migration.
    cr.execute("""
        UPDATE ir_ui_view
        SET active = FALSE
        WHERE name in ('account.analytic.account.invoice.form')
    """)

