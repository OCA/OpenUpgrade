# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_consumed(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE rating_rating rr
        SET consumed = True
        WHERE rating != -1
        """)
    openupgrade.logged_query(
        env.cr, """
            UPDATE rating_rating rr
            SET rating = 0
            WHERE rating = -1
            """)


@openupgrade.migrate()
def migrate(env, version):
    update_consumed(env)
