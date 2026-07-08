# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_slides", "19.0.2.7/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["website_slides.mail_activity_data_access_request"],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        ["mail_notification_channel_invite"],
        ["arch_db"],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        [
            "mail_template_channel_completed",
            "mail_template_channel_shared",
            "slide_template_published",
            "slide_template_shared",
        ],
        ["body_html"],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        [
            "rule_slide_channel_visibility_public_user",
            "rule_slide_channel_visibility_signed_in_user",
            "rule_slide_slide_public_user",
            "rule_slide_slide_signed_in_user",
        ],
        ["name"],
    )
