# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
import logging
logger = logging.getLogger('OpenUpgrade.stock')

@openupgrade.migrate()
def migrate(cr, version):

    # Set partners which will help to see all subscribed channels in
    # Channels sub-menu under Discuss Menu
    cr.execute("""
    INSERT INTO mail_channel_partner (channel_id, partner_id) 
    SELECT res_id, partner_id from mail_followers
    WHERE res_model = 'mail.channel'
    """)
