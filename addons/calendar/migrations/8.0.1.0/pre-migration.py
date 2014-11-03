# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(
        cr, [('crm_meeting_type', 'calendar_event_type')])
    openupgrade.rename_columns(
        cr,
        {
            'calendar_event': [
                ('end_date', 'date_final'),
                ('select1', 'month_by'),
                ('date', 'start_datetime'),
                ('date_deadline', 'stop_datetime'),
                ('alarm_id', None),
                ('base_calendar_alarm_id', None),
                ('base_calendar_url', None),
                ('exdate', None),
                ('exrule', None),
                ('month_list', None),
                ('organizer', None),
                ('organizer_id', None),
                ('sequence', None),
                ('vtimezone', None),
            ],
            'calendar_alarm': [
                ('action', 'type'),
                ('active', None),
                ('alarm_id', None),
                ('attach', None),
                ('description', None),
                ('duration', None),
                ('event_date', None),
                ('event_end_date', None),
                ('model_id', None),
                ('repeat', None),
                ('res_id', None),
                ('state', None),
                ('trigger_date', None),
                ('trigger_duration', 'duration'),
                ('trigger_interval', 'interval'),
                ('trigger_occurs', None),
                ('trigger_related', None),
                ('user_id', None),
            ],
            'calendar_attendee': [
                ('cutype', None),
                ('dir', None),
                ('member', None),
                ('ref', None),
                ('role', None),
                ('rsvp', None),
                ('user_id', None),
            ],
        })
    # we create and prefill this fields (with bogus data, they will be
    # recomputed during post-migrate in order to avoid errors when creating
    # not null constraints
    cr.execute(
        '''alter table calendar_event
        add column start timestamp without time zone,
        add column stop timestamp without time zone''')
    cr.execute(
        '''update calendar_event
        set start=start_datetime, stop=stop_datetime''')
