# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2014
#            Pedro M. Baeza (pedro.baeza@serviciosbaeza.com)
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

@openupgrade.migrate()
def migrate(cr, version):
    # look for account.analytic.plan.line without plan_id
    cr.execute("""
        SELECT id
        FROM account_analytic_plan_line
        WHERE plan_id is NULL""")
    record = cr.fetchone()
    if record:
        # Create support plan 
        logged_query(cr, ("""
            INSERT INTO account_analytic_plan ('name')
            FROM account_analytic_plan_line
            VALUES ('OpenUpgrade migration plan')"""))
        # Fill empty values with this new record value
        logged_query(cr, ("""
            UPDATE account_analytic_plan_line
            SET plan_id = 
                (SELECT id FROM account_analytic_plan 
                 WHERE NAME='OpenUpgrade migration plan')
            WHERE plan_id is NULL"""))
