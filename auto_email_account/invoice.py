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

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def action_number(self, cr, uid, ids):
        result=None
        context=None
        result=super(account_invoice, self).action_number(cr, uid, ids)
        part=self.read(cr, uid, ids ,['address_invoice_id'],context=None)[0]
        partner_address_id = part['address_invoice_id'][0]
        address_data= self.pool.get('res.partner.address').read(cr, uid, partner_address_id,[], context)
        if 'email' in address_data:
            if address_data['email']:
                email = address_data['email']
                smtpserver_id = self.pool.get('email.smtpclient').search(cr, uid, [], context=False)
                smtpserver = self.pool.get('email.smtpclient').browse(cr, uid, smtpserver_id, context=False)[0]
                body= "Your Invoice is Validated \n Please See the attachment"
                state = smtpserver.send_email(cr, uid, smtpserver_id, email,"Tiny ERP: Invoice validated",ids[0],'account.invoice','Invoice',body)
                if not state:
                    raise Exception, 'Varification Failed, Please check the Server Configuration!!!'        
        return result
account_invoice()