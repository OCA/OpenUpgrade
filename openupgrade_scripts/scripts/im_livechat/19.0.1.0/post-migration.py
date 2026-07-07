# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def chatbot_script_step_message(env):
    """
    Convert chatbot.script.step#message to html
    """
    openupgrade.copy_columns(env.cr, {"chatbot_script_step": [("message", None, None)]})
    openupgrade.convert_field_to_html(
        env.cr, "chatbot_script_step", "message", "message", translate=True
    )


def im_livechat_channel_rule_chatbot_enabled_condition(env):
    """
    Set im_livechat_channel_rule#chatbot_enabled_condition depending on
    chatbot_only_if_no_operator
    """
    env.cr.execute(
        """
        UPDATE
            im_livechat_channel_rule
        SET
            chatbot_enabled_condition='only_if_no_operator'
        WHERE
            chatbot_only_if_no_operator
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "im_livechat", "19.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "im_livechat",
        [
            "livechat_email_template",
        ],
        ["body_html"],
    )
    chatbot_script_step_message(env)
    im_livechat_channel_rule_chatbot_enabled_condition(env)
