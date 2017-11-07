# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def convert_campaigns_to_utm(env):
    """Link ``mail.mass_mailing.campaign`` to ``utm.campaign`` records.

    This method creates one ``utm.campaign`` record for each
    ``mail.mass_mailing.campaign`` that has none, and fills its name if it had
    it empty.
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
    convert_campaigns_to_utm(env)
