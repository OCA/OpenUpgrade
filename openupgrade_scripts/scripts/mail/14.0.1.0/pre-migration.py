# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_mail_tracking_value_field(env):
    """Now the field is a hard many2one reference, so we need to traverse the
    ir.model.fields record and fill it.

    As the column is required, we do it on pre, and we need also to remove those
    records whose field reference doesn't exist anymore.
    """
    openupgrade.logged_query(env.cr, "ALTER TABLE mail_tracking_value ADD field int4")
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_tracking_value mtv
        SET field = imf.id
        FROM ir_model_fields imf
        JOIN mail_message mm ON imf.model = mm.model
        WHERE imf.name = mtv.{} AND mtv.mail_message_id = mm.id
        """.format(
            openupgrade.get_legacy_name("field")
        ),
    )
    openupgrade.logged_query(
        env.cr, "DELETE FROM mail_tracking_value WHERE field IS NULL"
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(
        env.cr, [("email_template.preview", "mail.template.preview")]
    )
    openupgrade.rename_tables(
        env.cr, [("email_template_preview", "mail_template_preview")]
    )
    openupgrade.set_xml_ids_noupdate_value(env, "mail", ["mail_channel_rule"], True)
    openupgrade.rename_columns(env.cr, {"mail_tracking_value": [("field", None)]})
    fill_mail_tracking_value_field(env)
