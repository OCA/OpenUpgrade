# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association, Microcom
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
from openupgradelib import openupgrade


def map_priority(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('priority'),
        'priority',
        [('2', '1')],
        table='project_task', write='sql')


def map_template_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'),
        'state',
        [('template', 'draft')],
        table='project_project', write='sql')


def copy_user_id(cr):
    openupgrade.logged_query(cr, """
        UPDATE project_project
        SET user_id = aaa.user_id
        FROM account_analytic_account aaa
        WHERE aaa.id = project_project.analytic_account_id
        """)


@openupgrade.migrate()
def migrate(cr, version):
    # map_priority(cr)
    map_template_state(cr)
    copy_user_id(cr)
    map_priority(cr)
    openupgrade.convert_field_to_html(
        cr, 'project_task', openupgrade.get_legacy_name('description'),
        'description'
    )
