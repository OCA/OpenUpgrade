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

column_renames = {
    'project_issue': [
        ('version_id', None),
    ],
    'project_issue_project_tags_rel': [
        ('project_category_id', 'project_tags_id'),
    ],
}

table_renames = [
    (
        'project_category_project_issue_rel',
        'project_issue_project_tags_rel',
    ),
]

xmlid_renames = [
    (
        'project_issue.project_issue_category_01',
        'project_issue.project_issue_tags_00'
    ),
    (
        'project_issue.project_issue_category_02',
        'project_issue.project_issue_tags_01'
    ),
    (
        'project_issue.project_issue_category_03',
        'project_issue.project_issue_tags_02'
    ),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
