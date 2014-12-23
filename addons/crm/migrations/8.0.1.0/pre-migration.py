# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, a suite of open source business apps
#    This module Copyright (C) 2014 Therp BV (<http://therp.nl>).
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

from openerp.openupgrade import openupgrade


xmlids = [
    ('crm.crm_case_channel_direct', 'crm.crm_medium_direct'),
    ('crm.crm_case_channel_email', 'crm.crm_medium_email'),
    ('crm.crm_case_channel_phone', 'crm.crm_medium_phone'),
    ('crm.crm_case_channel_website', 'crm.crm_medium_website'),
    ('crm.default_sales_alias', 'crm.mail_alias_lead_info'),
    ]

column_renames = {
    'crm_lead': [
        ('channel_id', 'medium_id'),
        ('type_id', 'campaign_id'),
        ('priority', None),
        ],
    'crm_phonecall': [
        ('priority', None),
        ],
    }


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_models(
        cr, [
            ('crm.case.channel', 'crm.tracking.medium'),
            ('crm.case.resource.type', 'crm.tracking.campaign'),
            ])
    openupgrade.rename_columns(
        cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlids)
