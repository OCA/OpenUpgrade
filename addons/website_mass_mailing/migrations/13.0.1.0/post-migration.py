# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_mailing_list_website_popup_ids(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO website_mass_mailing_popup
        (create_date, write_date, create_uid, write_uid, mailing_list_id,
         popup_content)
        SELECT create_date, write_date, create_uid, write_uid, id, popup_content
        FROM mailing_list
        WHERE popup_content IS NOT NULL
        RETURNING id, mailing_list_id"""
    )
    # Handle translations
    for row in env.cr.fetchall():
        env.cr.execute(
            """UPDATE ir_translation
            SET name='website.mass_mailing.popup,popup_content',
                res_id = %s
            WHERE name='mail.mass_mailing.list,popup_content'
                AND res_id = %s""",
            (row[0], row[1]),
        )


@openupgrade.migrate()
def migrate(env, version):
    fill_mailing_list_website_popup_ids(env)
