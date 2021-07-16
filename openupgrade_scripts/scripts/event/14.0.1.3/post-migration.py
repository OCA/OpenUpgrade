# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_event_event_states_to_stages(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event event
        SET stage_id = stage.id
        FROM event_stage stage
        WHERE stage.name = 'New' AND event.state = 'draft'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event event
        SET stage_id = stage.id
        FROM event_stage stage, event_event event2
        LEFT JOIN event_registration evr ON evr.event_id = event2.id
        WHERE stage.name = 'Booked' AND event.state = 'confirm'
            AND evr.id IS NULL OR evr.state IN ('draft', 'cancel')
            AND event.id = event2.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event event
        SET stage_id = stage.id
        FROM event_stage stage, event_event event2
        JOIN event_registration evr ON evr.event_id = event2.id
        WHERE stage.name = 'Announced' AND event.state = 'confirm'
            AND evr.state IN ('open', 'done')
            AND event.id = event2.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event event
        SET stage_id = stage.id
        FROM event_stage stage
        WHERE stage.name = 'Ended' AND event.state = 'done'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event event
        SET stage_id = stage.id
        FROM event_stage stage
        WHERE stage.name = 'Cancelled' AND event.state = 'cancel'""",
    )


@openupgrade.migrate()
def migrate(env, version):
    map_event_event_states_to_stages(env)
    openupgrade.load_data(env.cr, "event", "14.0.1.3/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "event.event_type_data_online",
            "event.event_type_data_physical",
            "event.event_registration_portal",
        ],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "event",
        [
            "event_registration_mail_template_badge",
            "event_reminder",
            "event_subscription",
        ],
    )
