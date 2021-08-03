# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_bill_type(env):
    openupgrade.logged_query(
        env.cr,
        """ UPDATE
                        project_project
                    SET
                        bill_type = 'customer_project'
                    WHERE
                        sale_order_id is not null
                """,
    )


def fill_allow_billable(env):
    timesheet_product_id = env.ref("sale_timesheet.time_product", False)
    openupgrade.logged_query(
        env.cr,
        """ UPDATE
                        project_project
                    SET
                        allow_billable = 't',
                        timesheet_product_id = %s
                    WHERE
                        pricing_type is not null
                """,
        (timesheet_product_id.id,),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_bill_type(env)
    fill_allow_billable(env)
    # Load noupdate changes
    openupgrade.load_data(env.cr, "sale_timesheet", "14.0.1.0/noupdate_changes.xml")
