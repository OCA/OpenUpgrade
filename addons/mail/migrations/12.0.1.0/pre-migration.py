# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    'res_partner': [
        ('opt_out', None),
    ],
}

_field_renames = [
    ('mail.activity.type', 'mail_activity_type', 'days', 'delay_count'),
    # for preserving filters et al that have the same meaning
    ('res.partner', 'res_partner', 'opt_out', 'is_blacklisted'),
]


def fill_mail_message_add_sign_default(env):
    """Faster way to fill this new field"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE mail_message
        ADD COLUMN add_sign boolean
        DEFAULT TRUE""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE mail_message ALTER COLUMN add_sign DROP DEFAULT""",
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    fill_mail_message_add_sign_default(env)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'mail', ['mail_channel_rule'], False)
