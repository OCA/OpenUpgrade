# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#    (<http://www.akretion.com>).
#    @author: Onestein <www.onestein.nl>
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


from openerp import pooler, SUPERUSER_ID as uid
from openerp.openupgrade import openupgrade, openupgrade_80


def mail_mail_to_mail_message_migration(cr, uid, pool):
    """
    The following fields have been moved from mail.mail to mail.message
      * mail_server_id
      * reply_to
    Get the mail.message from the mail.mail object and transfer the data that
    way.
    """
    legacy_server_id = openupgrade.get_legacy_name('mail_server_id')
    legacy_reply_to = openupgrade.get_legacy_name('reply_to')
    openupgrade.logged_query(cr, """
UPDATE mail_message AS a
SET %s = %s, %s = %s
FROM mail_mail AS b WHERE a.id = b.mail_message_id
""" % ('mail_server_id', legacy_server_id, 'reply_to', legacy_reply_to, ))


def map_notify_email(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('notification_email_send'),
        'notify_email',
        [('all', 'always'), ('comment', 'always'),
         ('email', 'always'), ('none', 'none')],
        table='res_partner', write='sql')


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)

    map_notify_email(cr)
    mail_mail_to_mail_message_migration(cr, uid, pool)
    openupgrade_80.set_message_last_post(
        cr, uid, pool, ['res.partner', 'mail.group'])
    openupgrade_80.update_aliases(cr, pool, 'mail.group', True)
    openupgrade_80.update_aliases(cr, pool, 'res.users', True)
    openupgrade.load_data(
        cr, 'mail', 'migrations/8.0.1.0/noupdate_changes.xml')
