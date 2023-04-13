# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def set_mailing_medium(env):
    """The field column exists before migration so the new compute behavior won't be
    triggered. We need to load the values as it's required in the view"""
    medium_email = env.ref("utm.utm_medium_email").id
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE mailing_mailing
        SET medium_id = {medium_email}
        WHERE mailing_type = 'mail'
        AND medium_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    set_mailing_medium(env)
