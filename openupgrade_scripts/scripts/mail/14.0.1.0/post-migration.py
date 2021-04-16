# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_mail_tracking_value_field(env):
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


@openupgrade.migrate()
def migrate(env, version):
    fill_mail_tracking_value_field(env)
    openupgrade.load_data(env.cr, "mail", "14.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "mail.mail_followers_read_write_own",
        ],
    )
