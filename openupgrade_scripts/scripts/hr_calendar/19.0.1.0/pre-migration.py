# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade

deleted_xmlids = [
    "hr_calendar.view_calendar_event_form",
    "hr_calendar.view_calendar_event_form_quick_create",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
