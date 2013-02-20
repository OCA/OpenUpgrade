# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv

class res_partner_mail(osv.Model):
    """ Update partner to add a field about notification preferences """
    _name = "res.partner"
    _inherit = ['res.partner', 'mail.thread']
    _mail_flat_thread = False

    _columns = {
        'notification_email_send': fields.selection([
            ('all', 'All feeds'),
            ('comment', 'Comments and Emails'),
            ('email', 'Emails only'),
            ('none', 'Never')
            ], 'Receive Feeds by Email', required=True,
            help="Choose in which case you want to receive an email when you "\
                  "receive new feeds."),
    }

    _defaults = {
        'notification_email_send': lambda *args: 'comment'
    }

    def message_post(self, cr, uid, thread_id, **kwargs):
        """ Override related to res.partner. In case of email message, set it as
            private:
            - add the target partner in the message partner_ids
            - set thread_id as None, because this will trigger the 'private'
                aspect of the message (model=False, res_id=False)
        """
        if isinstance(thread_id, (list, tuple)):
            thread_id = thread_id[0]
        if kwargs.get('type') == 'email':
            partner_ids = kwargs.get('partner_ids', [])
            if thread_id not in [command[1] for command in partner_ids]:
                partner_ids.append((4, thread_id))
            kwargs['partner_ids'] = partner_ids
            thread_id = False
        return super(res_partner_mail, self).message_post(cr, uid, thread_id, **kwargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
