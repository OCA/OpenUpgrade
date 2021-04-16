# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(
        env.cr, [("email_template.preview", "mail.template.preview")]
    )
    openupgrade.set_xml_ids_noupdate_value(env, "mail", ["mail_channel_rule"], True)
    openupgrade.update_module_moved_fields(
        env.cr, "mail.mail", ["description"], "website_mail", "mail"
    )
    openupgrade.update_module_moved_fields(
        env.cr, "mail.message", ["description"], "website_mail", "mail"
    )
    openupgrade.rename_columns(env.cr, {"mail_tracking_value": [("field", None)]})
