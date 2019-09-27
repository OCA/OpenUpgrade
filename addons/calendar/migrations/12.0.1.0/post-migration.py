# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'calendar', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'calendar', [
            'calendar_template_meeting_invitation',
            'calendar_template_meeting_changedate',
            'calendar_template_meeting_reminder',
        ],
    )
    event_calendar_type_xml_ids = [
        'calendar.categ_meet1',
        'calendar.categ_meet2',
        'calendar.categ_meet3',
        'calendar.categ_meet4',
        'calendar.categ_meet5',
    ]
    CalendarEvent = env['calendar.event']
    IrModelData = env['ir.model.data']
    for xml_id in event_calendar_type_xml_ids:
        record = env.ref(xml_id)
        if CalendarEvent.search([('categ_ids', '=', record.id)]):
            # delete only XML-ID, as type is used, but not "safely" detected
            module, name = xml_id.split('.')
            IrModelData.search([
                ('module', '=', module),
                ('name', '=', name),
            ]).unlink()
        else:
            openupgrade.delete_records_safely_by_xml_id(env, [xml_id])
