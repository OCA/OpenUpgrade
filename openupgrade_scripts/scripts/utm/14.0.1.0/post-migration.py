# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "utm.utm_campaign_christmas_special",
            "utm.utm_campaign_email_campaign_products",
            "utm.utm_campaign_email_campaign_services",
            "utm.utm_campaign_fall_drive",
            "utm.campaign_stage_1",
            "utm.campaign_stage_2",
            "utm.campaign_stage_3",
        ],
    )
