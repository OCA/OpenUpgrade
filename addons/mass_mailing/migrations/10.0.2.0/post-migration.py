# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Jairo Llopis
# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_garbage_records = [
    "mass_mailing.mass_mailing_marketing_user_access",
    "mass_mailing.mass_mailing_marketing_manager_access",
]


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
    openupgrade.load_data(
        env.cr, 'mass_mailing', 'migrations/10.0.2.0/noupdate_changes.xml',
    )
    # The OCA module mass_mailing_security_group was merged into mass_mailing
    # but we need to remove the record rules given by it
    openupgrade.delete_records_safely_by_xml_id(env, _garbage_records)
