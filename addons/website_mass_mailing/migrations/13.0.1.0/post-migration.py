# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_mailing_list_website_popup_ids(env):
    popup = env['website.mass_mailing.popup']

    sql = """
    SELECT id, {popup_content} 
    FROM mailing_list 
    WHERE {popup_content} IS NOT NULL
    """.format(popup_content=openupgrade.get_legacy_name('popup_content'))
    env.cr.execute(sql)
    rows = env.cr.fetchall()

    for row in rows:
        popup.create({
            'mailing_list_id': row[0],
            'popup_content': row[1]
        })


@openupgrade.migrate()
def migrate(env, version):
    fill_mailing_list_website_popup_ids(env)
