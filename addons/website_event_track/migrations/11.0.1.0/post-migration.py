# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def fill_event_track_stage_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE event_track et
        SET stage_id = ets.id
        FROM event_track_stage ets
        WHERE et.%s = lower(ets.name)
        """, (AsIs(openupgrade.get_legacy_name('state')),)
    )


def fill_event_track_partner_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE event_track et
        SET partner_id = rel.partner_id
        FROM (SELECT event_track_id, min(res_partner_id) as partner_id
              FROM event_track_res_partner_rel ep_rel
              JOIN res_partner rp ON ep_rel.res_partner_id = rp.id
              WHERE rp.active
              GROUP BY event_track_id) rel
        WHERE et.partner_id IS NULL AND rel.event_track_id = et.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_event_track_stage_id(env)
    fill_event_track_partner_id(env.cr)
