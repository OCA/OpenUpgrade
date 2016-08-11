# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        "update account_analytic_line l set issue_id=t.issue_id "
        "from hr_analytic_timesheet t where l.id=t.line_id")
