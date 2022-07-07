from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE res_company
            SET internal_project_id = leave_timesheet_project_id
        """,
    )
