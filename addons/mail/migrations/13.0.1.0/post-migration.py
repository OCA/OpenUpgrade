# Copyright 2020 Andrii Skrypka
# Copyright 2020 Opener B.V. (stefan@opener.amsterdam)
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, 'mail', 'migrations/13.0.1.0/noupdate_changes.xml')
    # Convert track_visibility value to tracking value in ir_model_fields
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_model_fields
        SET tracking = 100
        WHERE track_visibility IS NOT NULL
        """,
    )
    # Convert is_email value to notification_type value in mail_notification
    openupgrade.logged_query(
        env.cr,
        """ UPDATE mail_message_res_partner_needaction_rel
        SET notification_type = 'email'
        WHERE is_email; """)
    # Populate different message_type in mail_message following
    # https://github.com/OCA/OpenUpgrade/blob/d76498/addons/mail/models/mail_thread.py#L2188
    # https://github.com/OCA/OpenUpgrade/blob/d76498/addons/mail/models/mail_thread.py#L2192
    # to https://github.com/OCA/OpenUpgrade/blob/d76498/odoo/tools/mail.py#L442
    openupgrade.logged_query(
        env.cr,
        """ UPDATE mail_message
        SET message_type = 'user_notification'
        WHERE message_type = 'notification'
            AND model IS NULL
            AND res_id = 0
            AND message_id like '%openerp-message-notify%'""")
    # Populate missing read_date values mail.notification
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_message_res_partner_needaction_rel
        SET read_date = now() AT TIME ZONE 'UTC'
        WHERE is_read""",
    )
