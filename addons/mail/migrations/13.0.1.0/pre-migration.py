# Copyright 2020 Andrii Skrypka
# Copyright 2020 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_model_renames = [
    ('mail.blacklist.mixin', 'mail.thread.blacklist'),
]

_field_renames = [
    ('mail.channel', 'mail_channel', 'image', 'image_128'),
    ('mail.message', 'mail_message', 'layout', 'email_layout_xmlid'),
    ('mail.message', 'mail_message', 'needaction_partner_ids', 'notified_partner_ids'),
    ('mail.notification', 'mail_message_res_partner_needaction_rel', 'email_status', 'notification_status'),
    ('mail.tracking.value', 'mail_tracking_value', 'track_sequence', 'tracking_sequence'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_fields(env, _field_renames)
    # Fix image of mail.channel after renaming column to image_128
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment
        SET res_field = 'image_128'
        WHERE res_field = 'image' and res_model = 'mail.channel'
        """,
    )
