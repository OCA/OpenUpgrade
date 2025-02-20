# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def fill_related_stored_fields(env):
    openupgrade.logged_query(
        env.cr,
        """UPDATE event_booth eb
        SET price = ebc.price
        FROM event_booth_category ebc
        WHERE eb.booth_category_id = ebc.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE event_type_booth etb
        SET price = ebc.price
        FROM event_booth_category ebc
        WHERE etb.booth_category_id = ebc.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_related_stored_fields(env)
