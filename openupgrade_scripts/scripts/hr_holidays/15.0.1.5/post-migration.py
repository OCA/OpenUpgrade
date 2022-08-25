from openupgradelib import openupgrade


def fill_hr_leave_type_requires_allocation(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_type
        SET requires_allocation = 'no'
        WHERE allocation_type = 'no'""",
    )


def _map_hr_leave_state(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("cancel", "refuse")],
        table="hr_leave",
    )


def _map_hr_leave_allocation_state(env):
    env["hr.leave.allocation"].search([("state", "=", "validate1")]).activity_update()
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("validate1", "confirm")],
        table="hr_leave_allocation",
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_hr_leave_state(env)
    _map_hr_leave_allocation_state(env)
    openupgrade.load_data(env.cr, "hr_holidays", "15.0.1.5/noupdate_changes.xml")
