# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _mail_message_link_preview(env):
    """
    in v18, mail.link.preview linked directly to mail.message
    in v19, it's mail.link.preview <- mail.message.link.preview -> mail.message
    """
    env.cr.execute(
        """
        INSERT INTO
        mail_message_link_preview
        (link_preview_id, message_id, is_hidden)
        SELECT id, message_id, is_hidden FROM mail_link_preview
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "mail", "19.0.1.19/noupdate_changes.xml")
    _mail_message_link_preview(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "mail.ir_cron_discuss_users_settings_unmute",
            "mail.module_category_canned_response",
        ],
    )
