# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        'update account_analytic_line '
        'set task_id=work.task_id '
        'from '
        '(select w.task_id, t.line_id '
        'from project_task_work w '
        'join hr_analytic_timesheet t '
        'on w.hr_analytic_timesheet_id=t.id) work '
        'where work.line_id=account_analytic_line.id')
