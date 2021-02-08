# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


_field_renames = [
    ('im_livechat.channel', 'im_livechat_channel',
     'image_medium', 'image_128'),
]


def rename_image_attachments(env):
    for old, new in [("image_medium", "image_128")]:
        openupgrade.logged_query(
            env.cr, """
            UPDATE ir_attachment SET res_field = %s
            WHERE res_field = %s AND res_model = 'im_livechat.channel'""",
            (new, old),
        )


def fill_mail_channel_livechat_operator_id(env):
    # Done in pre-migration to avoid sql constraint
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE mail_channel
        ADD COLUMN livechat_operator_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_channel mc
        SET livechat_operator_id = ru.partner_id
        FROM im_livechat_channel ilc
        JOIN im_livechat_channel_im_user ilciu ON ilciu.channel_id = ilc.id
        JOIN res_users ru ON ru.id = ilciu.user_id
        WHERE mc.livechat_channel_id = ilc.id
            AND mc.livechat_operator_id IS NULL"""
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    if openupgrade.column_exists(
            env.cr, "im_livechat_channel", "website_description"):
        openupgrade.rename_xmlids(env.cr, [
            ("website_livechat.im_livechat_channel_data_website",
             "im_livechat.im_livechat_channel_data"),
        ])
    rename_image_attachments(env)
    fill_mail_channel_livechat_operator_id(env)
