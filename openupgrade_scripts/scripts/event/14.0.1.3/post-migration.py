# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_event_event_states_to_stages(env):
    def _map_state_to_stage(state, stage_xmlid):
        query = """
            UPDATE event_event event SET stage_id = imd.res_id
            FROM ir_model_data imd
            WHERE imd.module = 'event' AND imd.name = %s AND event.state = %s"""
        openupgrade.logged_query(env.cr, query, (stage_xmlid, state))

    _map_state_to_stage("draft", "event_stage_new")
    _map_state_to_stage("done", "event_stage_done")
    _map_state_to_stage("cancel", "event_stage_cancelled")
    _map_state_to_stage("confirm", "event_stage_announced")


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
