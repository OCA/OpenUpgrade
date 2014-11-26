# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

column_renames = {
    'crm_case_section': [
        ('allow_unlink', None),
    ],
    'crm_lead': [
        ('birthdate', None),
        ('categ_id', None),  # many2one -> many2many
        ('email', None),
        ('optin', None),
        ('optout', 'opt_out'),
        ('partner_address_id', None),
    ],
    'crm_meeting': [
        ('categ_id', None),
        ('date_action_last', None),
        ('date_action_next', None),
        ('email_from', None),
        ('partner_address_id', None),
        ('partner_id', None),
        ('recurrent_uid', None),
        ('section_id', None),
    ],
    'crm_phonecall': [
        ('partner_address_id', None),
    ],
    'crm_segmentation': [
        ('som_interval', None),
        ('som_interval_decrease', None),
        ('som_interval_default', None),
        ('som_interval_max', None),
    ],
}

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
