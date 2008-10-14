# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
import pooler
import netsvc
from tools.misc import UpdateableStr, UpdateableDict
import threading

class Invoice(osv.osv):
    _inherit = "account.invoice"
    
    def send_mail(self, db_name, uid, ids):
        db, pool = pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        
        result=None
        context=None
        
        smtp = self.pool.get('email.smtpclient')
        
        address = self.read(cr, uid, ids ,['address_invoice_id', 'number', 'name'],context=None)[0]
        email = smtp.selectAddress(cr, uid, partner=None, contact=[address['address_invoice_id'][0]])
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'account')
        
        if email:
            if smtpserver_id is False:
                raise Exception, 'Please check the Server Configuration !!!'
            
            smtpserver = self.pool.get('email.smtpclient').browse(cr, uid, smtpserver_id, context=False)
            
            body= smtpserver.body
            name = self.pool.get('res.partner.address').read(cr, uid, [address['address_invoice_id'][0]], ['name'])[0]['name'] or 'Customer'
            user = self.pool.get('res.users').read(cr, uid, [uid], ['name'])[0]['name'] or 'Tiny ERP'
            body = body.replace('__name__', name)
            body = body.replace('__user__', user)
            body = body.replace('__number__', str(address['number']))
            
            state = smtpserver.send_email(
                        cr, 
                        uid, 
                        [smtpserver_id], 
                        email, 
                        "Invoice  : " + str(address['number']),
                        ids,
                        body,
                        'account.invoice',
                        'Invoice'
                    )
            
            inv_data = self.read(cr, uid, ids ,['partner_id', 'amount_total'],context=None)
            partner_ids = inv_data[0]['partner_id']
            total = inv_data[0]['amount_total']
            
            event_obj = self.pool.get('res.partner.event')
            event_obj.create(cr, uid, {'name': 'Invoice: '+ str(address['number']),\
                    'partner_id': partner_ids[0],\
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),\
                    'user_id': uid,\
                    'partner_type': 'customer', 
                    'probability': 1.0,\
                    'planned_revenue': total,
                    'description' : body,
                    'document' : 'account.invoice,'+str(ids[0])})
            cr.commit()
            
            if not state:
                raise Exception, 'Verification Failed, Please check the Server Configuration!!!'
        else:
            model_id=self.pool.get('ir.model').search(cr, uid, [('model','=','account.invoice')], context=False)[0]
            if smtpserver_id:
                history = self.pool.get('email.smtpclient.history')
                history.create(
                    cr, 
                    uid,
                    {
                        'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),
                        'server_id' : smtpserver_id,
                        'name':'The Email is not sent because the Partner have no Email',
                        'email':'',
                        'model':model_id,
                        'resource_id':ids[0]
                    }
                )
        return {}
    
    def action_number(self, cr, uid, ids):
        super(Invoice, self).action_number(cr, uid, ids)
        cr.commit()
        thread1 = threading.Thread( target=self.send_mail , args=(cr.dbname, uid, ids))
        thread1.start()
        return True
        
Invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

