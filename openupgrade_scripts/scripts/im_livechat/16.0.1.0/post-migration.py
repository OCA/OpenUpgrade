from openupgradelib import openupgrade

_translations_to_delete = [
    "livechat_email_template",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "im_livechat", "16.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "im_livechat", _translations_to_delete
    )
