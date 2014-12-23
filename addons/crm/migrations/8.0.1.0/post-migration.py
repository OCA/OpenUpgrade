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

from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID
from openerp.openupgrade import openupgrade, openupgrade_80


@openupgrade.migrate()
def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)

    openupgrade.map_values(
        cr, 'priority', openupgrade.get_legacy_name('priority'),
        [('5', '0'), ('4', '1'), ('3', '2'), ('2', '3'), ('1', '4')],
        table='crm_lead')
    openupgrade.map_values(
        cr, 'priority', openupgrade.get_legacy_name('priority'),
        [('5', '0'), ('4', '0'), ('3', '1'), ('1', '2')],
        table='crm_phonecall')
    openupgrade.logged_query(
        cr, "UPDATE crm_phonecall SET state = %s WHERE state = %s",
        ('draft', 'pending'))

    # Set the date of the last update
    subtype_ids = (
        registry['ir.model.data'].get_object_reference(
            cr, SUPERUSER_ID, 'crm', 'mt_lead_stage')[1],
        registry['ir.model.data'].get_object_reference(
            cr, SUPERUSER_ID, 'crm', 'mt_salesteam_lead_stage')[1])

    # Update event tracking datetime fields
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, registry, ['crm.phonecall', 'crm.lead'])
    openupgrade.logged_query(
        cr,
        """
        UPDATE crm_lead l
        SET date_last_stage_update = COALESCE(
            (SELECT MAX(create_date) FROM mail_message m
             WHERE subtype_id in %s
                AND m.res_id = l.id),
            l.create_date)
        """, (subtype_ids,))

    # Move opportunity and phonecall to matching calendar_event
    openupgrade.logged_query(
        cr,
        """
        UPDATE calendar_event e
        SET opportunity_id = m.opportunity_id,
            phonecall_id = m.phonecall_id
        FROM crm_meeting m
        WHERE e.{} = m.id""".format(
            openupgrade.get_legacy_name('crm_meeting_id')))

    openupgrade.load_data(cr, 'crm', 'migrations/8.0.1.0/noupdate_changes.xml')
