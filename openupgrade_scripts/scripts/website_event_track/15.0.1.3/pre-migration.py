# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(
        env,
        [
            (
                "contact_email",
                "event.track",
                "event_track",
                "char",
                False,
                "website_event_track",
            ),
            (
                "contact_phone",
                "event.track",
                "event_track",
                "char",
                False,
                "website_event_track",
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE event_track et
        SET contact_email = rp.email, contact_phone = rp.phone
        FROM res_partner rp
        WHERE rp.id = et.partner_id
            AND (rp.email IS NOT NULL OR rp.phone IS NOT NULL)""",
    )
    openupgrade.rename_fields(
        env,
        [
            (
                "event.track.stage",
                "event_track_stage",
                "is_accepted",
                "is_visible_in_agenda",
            )
        ],
    )
