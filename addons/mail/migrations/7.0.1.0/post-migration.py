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
from openerp.openupgrade import openupgrade_70

logger = logging.getLogger('OpenUpgrade (mail)')

subtype_mapping = {
    'plain': (openupgrade.get_legacy_name('body_text'), plaintext2html),
    'mixed': (openupgrade.get_legacy_name('body_text'), plaintext2html),
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
            cr.execute("UPDATE mail_message SET body = %s WHERE id = %s", (body, row[0]))

def create_mail_mail(cr, pool):
    """
    Create mail.mail records for every mail.message in the system,
    because every mail.message in 6.1 is a conventional email.
    Also perform some other transformations.
    """
    message_obj = pool.get('mail.message')
    mail_obj = pool.get('mail.mail')
    message_ids = message_obj.search(
        cr, SUPERUSER_ID, [('email_from', '!=', False)])

    cr.execute("SELECT id, %s FROM mail_message" % (
            openupgrade.get_legacy_name('user_id')))
    user_ids = dict(cr.fetchall())

    for message_id in message_ids:
        message = message_obj.read(
            cr, SUPERUSER_ID, message_id, ['model', 'res_id', 'user_id', 'email_from'])
    
        # Set message type to notification
        write_vals = {
            'type': 'notification',
            }
        # Convert user_id to author partner
        if user_ids[message['id']]:
            write_vals['author_id'] = openupgrade_70.get_partner_id_from_user_id(
                cr, user_ids[message['id']])
        message_obj.write(cr, SUPERUSER_ID, message['id'], write_vals)
        
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
                    """, (name, message['id']))
            
        mail_id = mail_obj.create(
            cr, SUPERUSER_ID, {
                'mail_message_id': message['id'],
                'email_from': message['email_from'],
                })

    # Copy legacy fields from message table to mail table
    openupgrade.logged_query(cr,
        """
        UPDATE mail_mail
        SET body_html = msg.body,
            mail_server_id = msg.%(mail_server_id)s,
            email_to = msg.%(email_to)s,
            email_cc = msg.%(email_cc)s,
            reply_to = msg.%(reply_to)s,
            "references" = msg.%(references)s,
            state = msg.%(state)s,
            auto_delete = msg.%(auto_delete)s
        FROM mail_mail mail, mail_message msg
        WHERE mail.mail_message_id = msg.id
        """ % {
            'mail_server_id': openupgrade.get_legacy_name('mail_server_id'),
            'email_to': openupgrade.get_legacy_name('email_to'),
            'email_cc': openupgrade.get_legacy_name('email_cc'),
            'reply_to': openupgrade.get_legacy_name('reply_to'),
            'references': openupgrade.get_legacy_name('references'),
            'state': openupgrade.get_legacy_name('state'),
            'auto_delete': openupgrade.get_legacy_name('auto_delete'),
            })

    # Migrate m2o partner_id to m2m partner_ids
    openupgrade.m2o_to_m2m(
        cr, pool.get('mail.message'), 'mail_message', 'partner_ids',
        openupgrade.get_legacy_name('partner_id'))
            

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    convert_mail_bodies(cr, pool)
    create_mail_mail(cr, pool)
    openupgrade.load_data(cr, 'mail', 'migrations/7.0.1.0/data.xml')
