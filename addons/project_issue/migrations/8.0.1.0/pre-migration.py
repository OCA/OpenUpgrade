# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, a suite of business apps
# This module Copyright (C) 2014 Therp BV (<http://therp.nl>).
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

from openerp.openupgrade import openupgrade

column_renames = {'project_issue': [('priority', None)]}

xmlid_renames = [
    ('project_issue.mt_issue_closed', 'project_issue.mt_issue_ready'),
    ('project_issue.mt_issue_started', 'project_issue.mt_issue_assigned'),
    ('project_issue.mt_project_issue_started',
     'project_issue.mt_project_issue_assigned'),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
