# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Darshan Patel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_timesheet(cr):

    # Set is_timesheet account.analytic.line value from use_timesheets of
    # account.analytic.account
    cr.execute("""
        UPDATE account_analytic_line l
        SET is_timesheet = a.use_timesheets
        FROM account_analytic_account a
        WHERE a.id = l.account_id""")


@openupgrade.migrate()
def migrate(cr, version):
    set_timesheet(cr)

