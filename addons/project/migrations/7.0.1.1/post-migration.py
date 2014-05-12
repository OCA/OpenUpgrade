# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# This migration script copyright (C) 2014
# Pedro M. Baeza (pedro.baeza@serviciosbaeza.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID

def copy_state_from_analytic_account(cr):
    openupgrade.logged_query(cr, """
        UPDATE project_project
        SET state = account_analytic_account.%s
        FROM project_project
        INNER JOIN account_analytic_account
        ON account_analytic_account.id = project_project.analytic_account_id
        WHERE analytic_account_id is not NULL
        """ %(openupgrade.get_legacy_name('state')))

def short_name(name):
    """Keep first word(s) of name to make it small enough
       but distinctive"""
    if not name: return name
    # keep 7 chars + end of the last word
    keep_words = name[:7].strip().split()
    return ' '.join(name.split()[:len(keep_words)])

def createProjectAliases(cr, pool):
    alias_obj = pool.get('mail.alias')
    project_obj = pool.get('project.project')
    cr.execute("""
    SELECT project_project.id, account_analytic_account.name
    FROM project_project, account_analytic_account
    WHERE account_analytic_account.name is not NULL
    AND project_project.alias_id is NULL
    AND project_project.analytic_account_id = account_analytic_account.id
    """)
    for (id, name) in cr.fetchall():
        alias_id = alias_obj.create_unique_alias(cr, SUPERUSER_ID,
                              {'alias_name': "project+" + short_name(name)},
                              model_name='project.task')
        cr.execute("""
            UPDATE project_project
            SET alias_id=%s
            WHERE id=%s
            """, (alias_id, id))

@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return
    pool = pooler.get_pool(cr.dbname)
    copy_state_from_analytic_account(cr)
    createProjectAliases(cr, pool)
    openupgrade.logged_query(cr,'DROP VIEW project_vs_hours')
    openupgrade.load_data(cr, 'project', 'migrations/7.0.1.1/data.xml')
