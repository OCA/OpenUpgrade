# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association, Microcom
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
