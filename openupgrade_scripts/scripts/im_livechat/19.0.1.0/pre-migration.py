# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_copied_colums = {
    "chatbot_message": [
        ("user_script_answer_id", "user_raw_script_answer_id", None),
    ]
}

_deleted_xmlids = [
    "im_livechat.ir_rule_discuss_channel_group_im_livechat_group_manager",
    "im_livechat.ir_rule_discuss_channel_member_group_im_livechat_group_manager",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _copied_colums)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
    openupgrade.logged_query(env.cr, "DROP VIEW IF EXISTS im_livechat_report_operator")
