# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_bill_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project
        SET bill_type = 'customer_project'
        WHERE sale_order_id IS NOT NULL""",
    )


def fill_allow_billable(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project
        SET allow_billable = TRUE
        WHERE pricing_type IS NOT NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_bill_type(env)
    fill_allow_billable(env)
    openupgrade.load_data(env.cr, "sale_timesheet", "14.0.1.0/noupdate_changes.xml")
