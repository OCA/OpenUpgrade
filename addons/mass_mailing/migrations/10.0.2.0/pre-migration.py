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


def convert_campaigns_to_utm(env):
    """Link ``mail.mass_mailing.campaign`` to ``utm.campaign`` records.

    Odoo 8.0 had the ``name`` field directly in ``mail.mass_mailing.campaign``
    model. Odoo 9.0 had it there too, but it added ``_inherits`` from
    ``utm.campaign``, a weird move. Odoo 10.0 removed ``name`` from the model
    and relied on the linked ``utm.campaign``'s name, a more sensible move.

    The result is that if you had records coming from v8, they may appear with
    ``display_name`` as ``False`` to the superuser, and they may raise fake
    ``AccessError`` to other users, due to missing records in some low level
    inner joins that the ORM performs.

    This method creates one ``utm.campaign`` record for each
    ``mail.mass_mailing.campaign`` that has none, and fills its name.
    """
    mass = env["mail.mass_mailing.campaign"].search([
        "|", ("campaign_id", "=", False), ("campaign_id.name", "=", False),
    ])
    for one in mass:
        env.cr.execute(
            "SELECT name FROM mail_mass_mailing_campaign WHERE id = %s",
            (one.id,)
        )
        name = env.cr.fetchone()[0]
        if not one.campaign_id:
            one.campaign_id = env["utm.campaign"].create({
                "name": name,
            })
        elif not one.campaign_id.name:
            one.campaign_id.name = name


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, XMLID_RENAMES)
    fill_mass_mailing_sources(env)
    convert_campaigns_to_utm(env)
