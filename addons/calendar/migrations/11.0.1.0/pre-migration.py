# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
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


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    update_user_ids(cr)
    cleanup_translations(cr)
