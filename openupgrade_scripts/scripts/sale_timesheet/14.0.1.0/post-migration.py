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


def _fill_project_timesheet_product(env):
    """Fill the proper timesheet product once it has been populated in the DB.
    It should be done before filling `allow_billable` for avoiding the constraint.
    """
    product = env.ref("sale_timesheet.time_product")
    openupgrade.logged_query(
        env.cr,
        """UPDATE project_project pp
        SET timesheet_product_id = %s
        WHERE pp.pricing_type IS NOT NULL AND pp.allow_timesheets""",
        (product.id,),
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
    _fill_project_timesheet_product(env)
    fill_allow_billable(env)
    openupgrade.load_data(env.cr, "sale_timesheet", "14.0.1.0/noupdate_changes.xml")
