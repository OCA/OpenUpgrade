# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

model_renames = [
    ("mail.notification.web.push", "mail.push"),
    ("mail.partner.device", "mail.push.device"),
    ("mail.shortcode", "mail.canned.response"),
]

table_renames = [
    ("mail_notification_web_push", "mail_push"),
    ("mail_partner_device", "mail_push_device"),
    ("mail_shortcode", "mail_canned_response"),
]

field_renames = [
    ("mail.push", "mail_push", "user_device", "mail_push_device_id"),
]


def create_imd_entry_for_config_param(env):
    """
    If database has config parameter mail.restrict.template.rendering already
    set, create an ir.model.data entry for it to avoid trying to create it a
    second time
    """
    param = env["ir.config_parameter"].search(
        [("key", "=", "mail.restrict.template.rendering")]
    )
    if param and not env.ref(
        "mail.restrict_template_rendering", raise_if_not_found=False
    ):
        env["ir.model.data"].create(
            {
                "name": "restrict_template_rendering",
                "module": "mail",
                "model": param._name,
                "res_id": param.id,
                "noupdate": True,
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, model_renames)
    openupgrade.rename_tables(env.cr, table_renames)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "im_livechat.mail_shortcode_data_hello",
                "mail.mail_canned_response_data_hello",
            )
        ],
    )
    create_imd_entry_for_config_param(env)
