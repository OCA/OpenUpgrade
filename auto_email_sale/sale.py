# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
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
                    raise Exception, 'Verification Failed, No Server Defined!!!'
                smtpserver_id = sale_smtpserver_id or default_smtpserver_id
                smtpserver = self.pool.get('email.smtpclient').browse(cr, uid, smtpserver_id, context=False)[0]
                body= "Your order is confirmed... \n Please See the attachment..."
                state = smtpserver.send_email(cr, uid, smtpserver_id, email,"Tiny ERP: Sale Order Confirmed",ids,body,'sale.order','sale_order')
                if not state:
                    raise Exception, 'Verification Failed, Please check the Server Configuration!!!'
                return {}
            else:
                model_id=self.pool.get('ir.model').search(cr, uid, [('model','=','sale.order')], context=False)[0]
                if smtpserver_id:
                    self.pool.get('email.smtpclient.history').create \
                    (cr, uid, {'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),'server_id' : smtpserver_id[0],'name':'The Email is not sent because the Partner have no Email','email':'','model':model_id,'resource_id':ids[0]})
        return result
sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

