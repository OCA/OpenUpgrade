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
        result=super(account_invoice, self).action_number(cr, uid, ids)
        return result
account_invoice()