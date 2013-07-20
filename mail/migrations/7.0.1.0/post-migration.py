# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 credativ Ltd (<http://credativ.co.uk>)
#                          (C) 2013 Therp BV (<http://therp.nl>).
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

import logging
from openerp import pooler, SUPERUSER_ID
from openerp.tools.mail import html_sanitize, plaintext2html
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade (mail)')

subtype_mapping = {
    'plain': (openupgrade.get_legacy_name('body_text'), plaintext2html),
    'html': (openupgrade.get_legacy_name('body_html'), html_sanitize),
    }

def convert_mail_bodies(cr, pool):
    """
    Convert plain and html bodies to sanitized html.
    """
    message_obj = pool.get('mail.message')
    for subtype in subtype_mapping.keys():
        field, func = subtype_mapping[subtype]
        logger.info("converting %s messages", subtype)
        cr.execute(
            "SELECT id, %(field)s FROM mail_message "
            "WHERE %(msg_subtype)s = '%(subtype)s'" % {
                'msg_subtype': openupgrade.get_legacy_name('subtype'),
                'field': field,
                'subtype': subtype,
                })
        for row in cr.fetchall():
            body = func(row[1])
            cr.execute("UPDATE mail_message SET body = %s WHERE id = %s", body, row[0])

def create_mail_mail(cr, pool):
    """
    Create mail.mail records for every mail.message in the system,
    because every mail.message in 6.1 is a conventional email.
    Also perform some other transformations.
    """
    message_obj = pool.get('mail.message')
    mail_obj = pool.get('mail.mail')
    message_ids = message_obj.search([])
    messages = message_obj.read(message_obj.search([]), {}, '_classic_write')
    
    cr.execute("""SELECT user_id FROM mail_message""")
    user_ids = dict(cr.fetchall)

    for message in messages:
        # Set message type to notification
        write_vals = {
            'type': 'notification',
            }
        # Convert user_id to author partner
        if user_ids[message['id']]:
            write_vals['author_id'] = openupgrade.get_partner_id_from_user_id(
                cr, user_ids[message['id']])
        message_obj.write(message['id'], write_vals)
        
        # Set stored (but not recalculated) function field record_name
        if message['model'] and message['res_id']:
            model = pool.get(message['model'])
            if model:
                name = model.name_get(
                    cr, SUPERUSER_ID, [message['res_id']])[0][1]
                cr.execute(
                    """
                    UPDATE mail_message
                    SET record_name = %s
                    WHERE id = %s
                    """, name, message['id'])
            
        mail_id = mail_obj.create(
            {
                'mail_message_id': message['id'],
                })

    # Copy legacy fields from message table to mail table
    cr.execute(
        """
        UPDATE mail_mail
        SET mail.body_html = msg.body,
            mail.mail_server_id = msg.%(mail_server_id)s,
            mail.email_to = msg.%(email_to)s,
            mail.email_cc = msg.%(email_cc)s,
            mail.email_bcc = msg.%(email_bcc)s,
            mail.reply_to = msg.%(reply_to)s,
            mail.references = msg.%(references)s,
            mail.state = msg.%(state)s,
            mail.autodelete = msg.%(autodelete)s,
        FROM mail_mail mail, mail_message msg
        WHERE mail.mail_message_id = msg.id
        """ % {
            'mail_server_id': openupgrade.get_legacy_name('mail_server_id'),
            'email_to': openupgrade.get_legacy_name('email_to'),
            'email_cc': openupgrade.get_legacy_name('email_cc'),
            'email_bcc': openupgrade.get_legacy_name('email_bcc'),
            'reply_to': openupgrade.get_legacy_name('reply_to'),
            'references': openupgrade.get_legacy_name('references'),
            'state': openupgrade.get_legacy_name('state'),
            'autodelete': openupgrade.get_legacy_name('autodelete'),
            })

    # Migrate m2o partner_id to m2m partner_ids
    openupgrade.m2o_to_m2m(
        cr, 'mail.message', 'mail_message', 'partner_ids',
        openupgrade.get_legacy_name('partner_id'))
            

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    convert_mail_bodies(cr, pool)
    create_mail_mail(cr, pool)
    openupgrade.load_data(cr, 'mail', 'migrations/7.0.1.0/data.xml')
