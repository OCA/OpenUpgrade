# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def fill_event_track_stage_id(env):
    """Map to the new stage each of the old values of the state field."""
    state_mapping = {
        'draft': 'event_track_stage0',
        'confirmed': 'event_track_stage1',
        'announced': 'event_track_stage2',
        'published': 'event_track_stage3',
        'refused': 'event_track_stage4',
        'cancel': 'event_track_stage5',
    }
    for state, xml_id in state_mapping.items():
        openupgrade.logged_query(
            env.cr, """
            UPDATE event_track et
            SET stage_id = %s
            FROM event_track_stage ets
            WHERE et.%s = %s
            """, (
                env.ref('website_event_track.%s' % xml_id).id,
                AsIs(openupgrade.get_legacy_name('state')),
                state,
            ),
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
    # We need to fill related email if partner_id.email is filled for avoiding
    # error on message composer in the track
    openupgrade.logged_query(
        cr, """
        UPDATE event_track et
        SET partner_email = rp.email
        FROM res_partner rp
        WHERE et.partner_id = rp.id
            AND rp.email IS NOT NULL
            AND et.partner_email IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_event_track_stage_id(env)
    fill_event_track_partner_id(env.cr)
