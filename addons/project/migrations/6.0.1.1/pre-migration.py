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

import logging
from openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade: project')

renamed_columns = {
    'project_project': [
        ('category_id', 'analytic_account_id'),
        ('contact_id', 'openupgrade_legacy_contact_id'), # > aaa.contact_id
        ('date_start', 'openupgrade_legacy_date_start'), # > aaa.date_start
        ('date_end', 'openupgrade_legacy_date_end'),  # > aaa.date
        ('manager', 'openupgrade_legacy_manager'),  # > aaa.user_id
        ('name', 'openupgrade_legacy_name'), # > aaa.name
        ('notes', 'openupgrade_legacy_notes'), # > aaa.description
        ('parent_id', 'openupgrade_legacy_parent_id'), # aaa.parent_id of parent project's analytic account
        ('partner_id', 'openupgrade_legacy_partner_id'), # > aaa.partner_id
        ('state', 'openupgrade_legacy_state'), # > aaa.state (keys are equal)
        ],
    'project_task': [
        ('date_close', 'date_end'), # simple change of name
        ('type', 'type_id'), # name change
        ('parent_id', 'openupgrade_legacy_parent_id'), # m2o -> m2m parent_ids
        ],
    'res_company': [
        ('project_time_mode', 'openupgrade_legacy_project_time_mode'), # char selection -> m2o
        ],
    }

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, renamed_columns)
    logger.warn(
        "TODO: check whether project_task.date_deadline "
        "preserves content when type changes from datetime to date")
