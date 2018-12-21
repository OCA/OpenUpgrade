# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_resource_calendar_attendance_day_period(cr):
    openupgrade.logged_query(
        cr, """UPDATE resource_calendar_attendance
        SET day_period = CASE
            WHEN hour_from < 12
            THEN 'morning'
            ELSE 'afternoon' END
        """,
    )


def fill_resource_calendar_tz(cr):
    openupgrade.logged_query(
        cr, """UPDATE resource_calendar rc
        SET tz = rcl.%s
        FROM resource_calendar_leaves rcl
        WHERE rcl.calendar_id = rc.id AND rcl.%s IS NOT NULL
        """, (
            AsIs(openupgrade.get_legacy_name('tz')),
            AsIs(openupgrade.get_legacy_name('tz')),
        ),
    )


def fill_resource_resource_tz(cr):
    openupgrade.logged_query(
        cr, """UPDATE resource_resource rr
        SET tz = rp.tz
        FROM res_users ru
        LEFT JOIN res_partner rp ON ru.partner_id = rp.id
        WHERE rr.user_id = ru.id AND rp.tz IS NOT NULL
        """,
    )


@openupgrade.logging()
def fill_resource_calendar_hours_per_day(env):
    for calendar in env['resource.calendar'].search([]):
        calendar._onchange_hours_per_day()


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    fill_resource_calendar_attendance_day_period(cr)
    fill_resource_resource_tz(cr)
    fill_resource_calendar_tz(cr)
    fill_resource_calendar_hours_per_day(env)
    openupgrade.load_data(
        cr, 'resource', 'migrations/12.0.1.1/noupdate_changes.xml',
    )
