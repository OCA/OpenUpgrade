# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openupgrade import openupgrade

def set_timesheet_id(cr):
    """
    Migrate an integer field that represents a
    stock.incoterms' id field to a proper many2one
    (i.e. weed out obsolete ids)
    """
    cr.execute("""
        UPDATE
            project_task_work
        SET
            hr_analytic_timesheet_id = hr_analytic_timesheet.id
        FROM
            hr_analytic_timesheet
        WHERE
            openupgrade_legacy_hr_analytic_timesheet_id = hr_analytic_timesheet.id
        """)

@openupgrade.migrate()
def migrate(cr, version):
    set_timesheet_id(cr)
