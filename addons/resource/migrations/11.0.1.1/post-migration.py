# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_new_required_field_calendar_id(env):
    """ Create a calendar for each company and assign to all resources """
    for company in env['res.company'].search([]):
        company.write({
            'resource_calendar_id': env['resource.calendar'].create({
                'name': ('Standard 40 hours/week'),
                'company_id': company.id,
            }).id,
        })
    env.cr.execute("""
        UPDATE resource_resource SET calendar_id=subquery.resource_calendar_id
        FROM (
            SELECT r.id, r.company_id, c.resource_calendar_id
            FROM resource_resource r JOIN res_company c ON r.company_id = c.id
            WHERE r.calendar_id IS NULL
        ) AS subquery
        WHERE resource_resource.id = subquery.id;
    """)


def update_new_field_tz_for_linked_user(env):
    env.cr.execute("""
        UPDATE resource_calendar_leaves SET tz=subquery.tz
        FROM (
            SELECT rcl.id, p.tz
            FROM resource_calendar_leaves rcl
            JOIN resource_resource r ON rcl.resource_id = r.id
            JOIN res_users u ON r.user_id = u.id
            JOIN res_partner p ON u.partner_id = p.id
            WHERE r.user_id IS NOT NULL
        ) AS subquery
        WHERE resource_calendar_leaves.id = subquery.id;
    """)


@openupgrade.migrate()
def migrate(env, version):
    update_new_required_field_calendar_id(env)
    update_new_field_tz_for_linked_user(env)
