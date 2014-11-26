# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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

from openerp.openupgrade import openupgrade

def move_fetchmail_server_id(cr):
    """
    Fetchmail now relates to mail.mail, not mail.message
    """
    cr.execute(
        "UPDATE mail_mail SET fetchmail_server_id = "
        "       message.%(fetchmail_server_id)s "
        "FROM mail_mail mail, mail_message message "
        "WHERE mail.mail_message_id = message.id "
        "      AND message.%(fetchmail_server_id)s IS NOT NULL" % {
            'fetchmail_server_id': openupgrade.get_legacy_name(
                'fetchmail_server_id'),
            })

@openupgrade.migrate()
def migrate(cr, version):
    move_fetchmail_server_id(cr)
