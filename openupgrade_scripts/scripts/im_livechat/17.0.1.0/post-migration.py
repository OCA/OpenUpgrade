# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "im_livechat", "17.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "im_livechat",
        [
            "livechat_email_template",
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["im_livechat.im_livechat_rule_manager_read_all_mail_channel"]
    )
