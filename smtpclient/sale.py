from osv import fields,osv
import tools
import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        super(sale_order, self).write(cr, uid, ids, vals, context=context)
        if 'state' in vals:
            if vals['state'] in ['manual','progress']:
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
        return True
sale_order()