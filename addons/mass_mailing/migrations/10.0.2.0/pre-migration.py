# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

XMLID_RENAMES = [
    ('mass_mailing.group_website_popup_on_exit',
     'website_mass_mailing.group_website_popup_on_exit'),
]


def fill_missing_sources(env):
    env.cr.execute(
        "SELECT COUNT(*) FROM mail_mass_mailing WHERE source_id IS NULL"
    )
    if env.cr.fetchone()[0] == 0:
        return
    source = env['utm.source'].create({
        'name': "OpenUpgrade wildcard source",
    })
    openupgrade.logged_query(
        env.cr,
        """UPDATE mail_mass_mailing
        SET source_id = %s
        WHERE source_id IS NULL""",
        (source.id, )
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, XMLID_RENAMES)
    fill_missing_sources(env)
