# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

XMLID_RENAMES = [
    ('mass_mailing.group_website_popup_on_exit',
     'website_mass_mailing.group_website_popup_on_exit'),
]


def fill_mass_mailing_sources(env):
    """Odoo now inherits by delegation from utm.source and create a different
    record per mass mailing, using the name of the source as subject, so we
    need to pre-create a source for each record.

    WARNING: This replaces sources already set, but it's the only way to
    preserve the subject on the mass mailing and this binding is a feature
    hardly used on previous versions.
    """
    env.cr.execute("""SELECT id, name FROM mail_mass_mailing""")
    for row in env.cr.fetchall():
        source = env['utm.source'].create({
            'name': row[1],
        })
        env.cr.execute(
            """UPDATE mail_mass_mailing
            SET source_id = %s
            WHERE id = %s""",
            (source.id, row[0])
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, XMLID_RENAMES)
    fill_mass_mailing_sources(env)
