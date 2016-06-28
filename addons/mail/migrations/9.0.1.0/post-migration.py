# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    # Set partners which will help to see all subscribed channels in
    # Channels sub-menu under Discuss Menu
    cr.execute("""
    INSERT INTO mail_channel_partner (channel_id, partner_id)
    SELECT res_id, partner_id from mail_followers
    WHERE res_model = 'mail.channel'
    """)
    # notifications and stars are plain many2many fields by now
    cr.execute(
        'insert into mail_message_res_partner_needaction_rel '
        '(mail_message_id, res_partner_id) '
        'select message_id, partner_id from mail_notification '
        'where not is_read')
    cr.execute(
        'insert into mail_message_res_partner_starred_rel '
        '(mail_message_id, res_partner_id) '
        'select message_id, partner_id from mail_notification '
        'where starred')
