# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_utm_tag_rel(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO utm_tag_rel (tag_id, campaign_id)
        SELECT rel.tag_id, mmc.campaign_id
        FROM mail_mass_mailing_tag_rel rel
        JOIN mail_mass_mailing_campaign mmc ON mmc.id = rel.campaign_id"""
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, 'mail_mass_mailing_stage'):
        update_utm_tag_rel(env)
