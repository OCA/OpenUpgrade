# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv
import tools
import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict

class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

    def action_wait(self, cr, uid, ids):
        result = None
        context = None

        result = super(sale_order, self).action_wait(cr, uid, ids)

        part=self.read(cr, uid, ids ,['partner_order_id'],context=None)[0]
        partner_address_id = part['partner_order_id'][0]
        address_data= self.pool.get('res.partner.address').read(cr, uid, partner_address_id,[], context)
        if 'email' in address_data:
            sale_smtpserver_id = self.pool.get('email.smtpclient').search(cr, uid, [('type','=','sale')], context=False)
            if not sale_smtpserver_id:
                default_smtpserver_id = self.pool.get('email.smtpclient').search(cr, uid, [('type','=','default')], context=False)
            smtpserver_id = sale_smtpserver_id or default_smtpserver_id
            if address_data['email']:
                email = address_data['email']
                if not smtpserver_id:
                    raise osv.except_osv(_('Error'), _('Verification failed, No Server has been defined!'))
                smtpserver_id = sale_smtpserver_id or default_smtpserver_id
                body= _("Your order is confirmed.\nPlease, see the attachment.")
                                
                state = self.pool.get('email.smtpclient').send_email(cr, uid, smtpserver_id[0], email,_("OpenERP: Sale Order Confirmed"), body, reports=[('report.sale.order',ids)])
                if not state:
                    raise osv.except_osv(_('Error'), _('Verification failed. Please check the Server Configuration!'))
                return {}
            else:
                model_id=self.pool.get('ir.model').search(cr, uid, [('model','=','sale.order')], context=False)[0]
                if smtpserver_id:
                    self.pool.get('email.smtpclient.history').create \
                    (cr, uid, {'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),'server_id' : smtpserver_id[0],'name':_('The Email is not sent because the Partner have no Email'),'email':'','model':model_id,'resource_id':ids[0]})
        return result
sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

