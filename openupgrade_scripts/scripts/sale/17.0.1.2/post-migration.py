# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _sale_sale_order_(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
        SET locked = True
        WHERE temp_state = 'done'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        "ALTER TABLE sale_order DROP COLUMN temp_state",
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "sale", "17.0.1.2/noupdate_changes.xml")
