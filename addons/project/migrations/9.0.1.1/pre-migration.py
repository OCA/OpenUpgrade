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


column_copies = {
    'project_task': [
        ('description', None, None),
    ],
}

# These columns are kept even though they were removed in v9, in order to allow recovery by a future OCA module
column_renames = {
    'project_task': [
        ('reviewer_id', None),
    ],
    'project_task': [
        ('priority', None),
    ],
    'project_project': [
        ('state', None),
    ],
}

column_drops = [('project_config_settings', 'module_sale_service'),
                ('project_config_settings', 'module_pad'),
                ('project_config_settings', 'module_project_issue_sheet'),
                ('project_config_settings', 'group_time_work_estimation_tasks'),
                ('project_config_settings', 'module_project_timesheet'),
                ]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(
        cr, [('project_category', 'project_tags')])
    if openupgrade.column_exists(cr, 'project_project', 'members'):
        openupgrade.rename_columns(cr, {'project_project': [('members', None)]})
    # Removing transient tables to get rid of warnings
    openupgrade.drop_columns(cr, column_drops)
