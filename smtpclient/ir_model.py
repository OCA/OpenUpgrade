from osv import fields,osv
import tools
import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict

class res_company_address(osv.osv):
    _name = "res.company.address"
    _columns = {        
        'company_id' : fields.many2one('res.company', 'Company' , required=True),
        'email': fields.many2one('email.smtpclient', 'Email Address',  required=True),
        'name' : fields.selection([("default", "Default"),("inoice", "Invoice"),("sale","Sale"),("delivery","Delivery")], "Address Type",required=True)
    }
res_company_address()

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {        
        'addresses': fields.one2many('res.company.address', 'company_id', 'Email Addresses'),
    }
res_company()

class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    def action_wait(self, cr, uid, ids):
        result = None
        context = None
#        if not context:
#            context={}
        result = super(sale_order, self).action_wait(cr, uid, ids)
#        if 'state' in vals:
#            if vals['state'] in ['manual','progress']:
#                pass
        part=self.read(cr, uid, ids ,['partner_order_id'],context=None)[0]
        partner_address_id = part['partner_order_id'][0]
        address_data= self.pool.get('res.partner.address').read(cr, uid, partner_address_id,[], context)
        if 'email' in address_data:
            if address_data['email']:
                email = address_data['email']
                smtpserver_id = self.pool.get('email.smtpclient').search(cr, uid, [], context=False)
                smtpserver = self.pool.get('email.smtpclient').browse(cr, uid, smtpserver_id, context=False)[0]
                body= "Your order is confirmed \n Please See the attachment"
                state = smtpserver.send_email(cr, uid, smtpserver_id, email,"Tiny ERP: Sale Order Confirmed",ids[0],'sale.order','sale_order',body)
                if not state:
                    raise Exception, 'Varification Failed, Please check the Server Configuration!!!'
                return {}
        return result
sale_order()

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
