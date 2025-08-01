# Copyright 2025 L4 Tech S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def delete_noupdate_xml_ids(env):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "microsoft_calendar.microsoft_calendar_not_own_token_rule",
            "microsoft_calendar.microsoft_calendar_own_token_rule",
            "microsoft_calendar.microsoft_calendar_token_system_access",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    delete_noupdate_xml_ids(env)
