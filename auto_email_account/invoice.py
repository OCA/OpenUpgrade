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

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def send_mail(self, db_name, uid, ids):
        db, pool = pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        result=None
        context=None
        part=self.read(cr, uid, ids ,['address_invoice_id'],context=None)[0]            
        partner_address_id = part['address_invoice_id'][0]
        address_data= self.pool.get('res.partner.address').read(cr, uid, partner_address_id,[], context)
        if 'email' in address_data:
            account_smtpserver_id = self.pool.get('email.smtpclient').search(cr, uid, [('type','=','account')], context=False)
            if not account_smtpserver_id:
                default_smtpserver_id = self.pool.get('email.smtpclient').search(cr, uid, [('type','=','default')], context=False)
            smtpserver_id = account_smtpserver_id or default_smtpserver_id
            if address_data['email']:
                email = address_data['email'] 
                smtpserver_id = account_smtpserver_id or default_smtpserver_id               
                if not smtpserver_id:
                    raise Exception, 'Verification Failed, No Server Defined!!!'                
                smtpserver = self.pool.get('email.smtpclient').browse(cr, uid, smtpserver_id, context=False)[0]
                body= "Your Invoice is Validated \n Please See the attachment"
                state = smtpserver.send_email(cr, uid, smtpserver_id, email,"Tiny ERP: Invoice validated",ids,body,'account.invoice','Invoice')
                if not state:
                    raise Exception, 'Verification Failed, Please check the Server Configuration!!!'
                return {}
            else:                
                model_id=self.pool.get('ir.model').search(cr, uid, [('model','=','account.invoice')], context=False)[0]
                if smtpserver_id:
                    self.pool.get('email.smtpclient.history').create \
                    (cr, uid, {'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),'server_id' : smtpserver_id[0],'name':'The Email is not sent because the Partner have no Email','email':'','model':model_id,'resource_id':ids[0]})
        return {}
    
    def action_number(self, cr, uid, ids):
#        result = self.action_number1(cr, uid, ids)
#        if result:
        threads=[]
        thread2 = threading.Thread( target=self.action_number1 , args=( cr.dbname, uid, ids) )
        thread2.start()
        threads.append(thread2)
        thread1 = threading.Thread( target=self.send_mail , args=( cr.dbname, uid, ids) )
        thread1.start()
        threads.append(thread1)
#        for thread in threads:
#            thread.join()
        return {}
    
    def action_number1(self, db_name, uid, ids):
        db, pool = pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        result=None
        context=None
        result=super(account_invoice, self).action_number(cr, uid, ids)
        return result
#    
account_invoice()