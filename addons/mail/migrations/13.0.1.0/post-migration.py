# Copyright 2020 Andrii Skrypka
# Copyright 2020 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from odoo import fields


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
    # Populate missing message_type values in mail_message
    openupgrade.logged_query(
        env.cr,
        """ UPDATE mail_message
        SET message_type = 'user_notification'
        WHERE message_type = 'notification' and message_id like '%openerp-message-notify%'""")
    # Populate missing read_date values mail.notification
    env['mail.notification'].search([('is_read', '=', True)]).write({
        'read_date': fields.Datetime.today(),
    })
