# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_new_required_field_calendar_id(env):
    env.cr.execute("""
        UPDATE resource_resource SET calendar_id=subquery.resource_calendar_id
        FROM (
            SELECT r.id, r.company_id, c.resource_calendar_id
            FROM resource_resource r JOIN res_company c ON r.company_id = c.id
            WHERE r.calendar_id IS NULL
        ) AS subquery
        WHERE resource_resource.id = subquery.id;
    """)


@openupgrade.migrate()
def migrate(env, version):
    update_new_required_field_calendar_id(env)
