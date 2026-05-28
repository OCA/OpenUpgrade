from openupgradelib import openupgrade

# These noupdate record rules are removed in 19.0 but, being noupdate, are not
# swept by the standard module update; delete them by xml_id (record +
# ir_model_data) so the obsolete live-chat-manager channel access doesn't linger.
_obsolete_rule_xmlids = [
    "im_livechat.ir_rule_discuss_channel_group_im_livechat_group_manager",
    "im_livechat.ir_rule_discuss_channel_member_group_im_livechat_group_manager",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _obsolete_rule_xmlids)
