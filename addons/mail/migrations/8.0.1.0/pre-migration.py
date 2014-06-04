# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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


column_renames = {
    'res_partner': [
        ('notification_email_send', 'notify_email'),

    ],
    'mail_mail': [
        ('email_from', None),
        # The following fields are to be moved to mail_message in post
        ('mail_server_id', None),
        ('reply_to', None),
    ]
}


def partner_notify_migration(cr):
    """The selection values 'all', 'comment' and 'email' got replaced by
    'always', 'never' is still 'never'"""
    openupgrade.logged_query(cr, """
UPDATE res_partner
SET notify_email = 'always'
WHERE notify_email IN ('all', 'comment', 'email')""")


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    partner_notify_migration(cr)
