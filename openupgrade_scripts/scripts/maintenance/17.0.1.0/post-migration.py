# Copyright 2024-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_deleted_xml_records = ["maintenance.mail_alias_equipment"]


def _maintenance_plan(env):
    """Compatibility with maintenance_plan, we convert the request and
    the recurrence field the way it is done in core.
    """
    if openupgrade.column_exists(env.cr, "maintenance_request", "maintenance_plan_id"):
        # Update all the data of the linked requests
        openupgrade.logged_query(
            env.cr,
            """UPDATE maintenance_request mr
            SET recurring_maintenance = True,
            repeat_interval = COALESCE(mp.interval, 1),
            repeat_unit = COALESCE(mp.interval_step, 'year'),
            repeat_type='until',
            repeat_until = (
                CURRENT_DATE + (''
                || COALESCE(mp.maintenance_plan_horizon, 1) || ' '
                || COALESCE(mp.planning_step, 'year'))::interval
            )::date
            FROM maintenance_plan mp
            WHERE mr.maintenance_plan_id = mp.id""",
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "maintenance", "17.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _maintenance_plan(env)
