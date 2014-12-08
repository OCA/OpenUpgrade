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
from openerp.openupgrade import openupgrade, openupgrade_80
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


def import_crm_meeting(cr):
    '''
    merge crm.meeting records into plain calendar events, record crm.meeting's
    id in get_legacy_name('crm_meeting_id') to correct references in modules
    using crm.meeting before.
    Finally, update chatter.
    '''
    cr.execute(
        'alter table calendar_event add column %s int' % (
            openupgrade.get_legacy_name('crm_meeting_id'),
        )
    )
    cr.execute(
        '''insert into calendar_event
        (%s, create_uid, create_date, write_date, write_uid, name,
         state, allday,
         duration, description, class, location, show_as,
         rrule, rrule_type, recurrency, recurrent_id, recurrent_id_date,
         end_type, interval, count, mo, tu, we, th, fr, sa, su,
         day, week_list, byday, user_id, active,
         -- those are actually different
         start, stop, start_date, start_datetime,
         stop_date,
         stop_datetime, final_date,
         month_by)
        select
        id, create_uid, create_date, write_date, write_uid, name,
        state, allday,
        duration, description, class, location, show_as,
        rrule, rrule_type, recurrency, recurrent_id, recurrent_id_date,
        end_type, interval, count, mo, tu, we, th, fr, sa, su,
        day, week_list, byday, user_id, active,
        -- those are actually different
        date, date, date, date,
        coalesce(date + interval '1 hour' * duration, date),
        coalesce(date + interval '1 hour' * duration, date), end_date,
        select1
        from crm_meeting''' % (
            openupgrade.get_legacy_name('crm_meeting_id'),
        )
    )
    cr.execute(
        '''insert into calendar_event_res_partner_rel
        (calendar_event_id, res_partner_id)
        select
        calendar_event.id, partner_id
        from crm_meeting_partner_rel join calendar_event
        on %s=crm_meeting_partner_rel.meeting_id''' % (
            openupgrade.get_legacy_name('crm_meeting_id'),
        )
    )
    # there's a chance we still have the old constraint because
    # the values we update now caused the new constrained to be invalid
    cr.execute(
        '''alter table meeting_category_rel
        drop constraint meeting_category_rel_event_id_fkey''')
    cr.execute(
        '''update meeting_category_rel
        set event_id=calendar_event.id
        from calendar_event where event_id=%s''' % (
            openupgrade.get_legacy_name('crm_meeting_id'),
        )
    )
    # recreate the constraint as odoo would do it
    cr.execute(
        '''alter table meeting_category_rel
        add constraint meeting_category_rel_event_id_fkey
        foreign key (event_id) references calendar_event(id)
        on delete cascade''')
    # attendees now refer to their event in a m2o field
    cr.execute(
        '''update calendar_attendee
        set event_id=calendar_event.id
        from meeting_attendee_rel
        join calendar_event
        on %s=meeting_attendee_rel.event_id
        where attendee_id=calendar_attendee.id''' % (
            openupgrade.get_legacy_name('crm_meeting_id'),
        )
    )
    # and update chatter
    cr.execute(
        '''update mail_message
        set model='calendar.event', res_id=calendar_event.id
        from calendar_event
        where model='crm.meeting' and res_id=%s''' % (
            openupgrade.get_legacy_name('crm_meeting_id'),
        )
    )


def recompute_date_fields(cr):
    '''calculate stop_date{,time} from start_datetime + duration'''
    cr.execute(
        '''update calendar_event set
        start_date = start_datetime,
        stop_date = start_datetime + interval '1 hour' * duration,
        stop_datetime = start_datetime + interval '1 hour' * duration''')


def migrate_attendees(cr):
    '''attendees were linked by a many2many relation before'''
    cr.execute(
        '''update calendar_attendee
        set event_id=event_attendee_rel.event_id
        from event_attendee_rel
        where attendee_id=calendar_attendee.id'''
    )


def migrate_alarms(cr):
    '''now alarms are only defined in relation to the events they are attached
    to'''
    pool = RegistryManager.get(cr.dbname)
    calendar_event_model_id = pool['ir.model.data'].xmlid_to_res_id(
        cr, SUPERUSER_ID,
        'calendar.model_calendar_event', raise_if_not_found=True)
    cr.execute(
        '''insert into calendar_alarm_calendar_event_rel
        (calendar_event_id, calendar_alarm_id)
        select
        %s, calendar_alarm.id
        from calendar_alarm
        where %s=%s
        ''' % (
            openupgrade.get_legacy_name('res_id'),
            openupgrade.get_legacy_name('model_id'),
            calendar_event_model_id
        )
    )
    crm_meeting_model_id = pool['ir.model.data'].xmlid_to_res_id(
        cr, SUPERUSER_ID,
        'calendar.model_crm_meeting', raise_if_not_found=True)
    cr.execute(
        '''insert into calendar_alarm_calendar_event_rel
        (calendar_event_id, calendar_alarm_id)
        select
        calendar_event.id, calendar_alarm.id
        from calendar_alarm join calendar_event
        on %s=%s
        where %s=%s
        ''' % (
            openupgrade.get_legacy_name('res_id'),
            openupgrade.get_legacy_name('crm_meeting_id'),
            openupgrade.get_legacy_name('model_id'),
            crm_meeting_model_id
        )
    )


@openupgrade.migrate()
def migrate(cr, version):
    recompute_date_fields(cr)
    import_crm_meeting(cr)
    # now we filled new fields, recalculate some stored fields
    pool = RegistryManager.get(cr.dbname)
    calendar_event = pool['calendar.event']
    for field in ['start', 'stop', 'display_start']:
        calendar_event._update_store(cr, calendar_event._columns[field], field)
    migrate_attendees(cr)
    migrate_alarms(cr)
    # map renamed and deprecated reminder actions to 'notification'
    cr.execute(
        '''update calendar_alarm
        set type='notification'
        where type in ('audio', 'display', 'procedure')'''
    )
    # map renamed event states
    cr.execute(
        '''update calendar_event
        set state='draft' where state in ('cancelled', 'tentative')''')
    cr.execute(
        '''update calendar_event
        set state='open' where state in ('confirmed')''')
    # map renamed attendee states
    cr.execute(
        '''update calendar_attendee
        set state='needsAction' where state in ('needs-action')''')
    # load modified noupdate data
    openupgrade.load_data(cr, 'calendar', 'migrations/8.0.1.0/data.xml')
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, pool, ['calendar.event'])
