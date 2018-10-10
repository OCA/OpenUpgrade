# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_user_ids(cr):
    """
    Now user_id is required, set it to the one who created the entry
    """
    cr.execute("""
        UPDATE calendar_contacts SET user_id = create_uid
        WHERE user_id IS NULL;
    """)


def cleanup_translations(cr):
    """
    Cleanup translations of adopted templates
    """

    updated_templates = (
        'calendar_template_meeting_reminder',
        'calendar_template_meeting_changedate',
        'calendar_template_meeting_invitation',
    )

    openupgrade.delete_record_translations(cr, 'calendar', updated_templates)


def set_calendar_event_res_model(env):
    """This pre-creates before ORM related computation the field `res_model`,
    for avoiding an error when writing back the value on virtual records
    created by recurring events. No need of writing any possible value, as
    this is a new feature not available in v10.

    If the OCA module `mail_activity_calendar` was installed in
    previous version this field would already exist, thus no need to
    pre-create it.
    """
    if not openupgrade.column_exists(env.cr, 'calendar_event', 'res_model'):
        openupgrade.add_fields(
            env, [
                ('res_model', 'calendar.event', 'calendar_event', 'char',
                 False, 'calendar'),
            ],
        )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    update_user_ids(cr)
    cleanup_translations(cr)
    set_calendar_event_res_model(env)
