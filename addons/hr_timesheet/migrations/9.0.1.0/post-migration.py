# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Darshan Patel
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_timesheet(cr):

    # Set is_timesheet account.analytic.line value from use_timesheets of
    # account.analytic.account
    cr.execute("""
        UPDATE account_analytic_line aal
        SET is_timesheet = TRUE
        FROM hr_analytic_timesheet hat
        WHERE hat.line_id = aal.id
    """)


@openupgrade.migrate()
def migrate(cr, version):
    set_timesheet(cr)
