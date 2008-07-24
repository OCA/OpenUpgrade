# -*- encoding: utf-8 -*-
from osv import fields,osv

class EmailAddress(osv.osv):
    _name = "res.company.address"
    _columns = {        
        'company_id' : fields.many2one('res.company', 'Company' , required=True),
        'email': fields.many2one('email.smtpclient', 'Email Address',  required=True),
        'name' : fields.selection([("default", "Default"),("inoice", "Invoice"),("sale","Sale"),("delivery","Delivery")], "Address Type",required=True)
    }
EmailAddress()

class Company(osv.osv):
    _inherit = "res.company"
    _columns = {        
        'addresses': fields.one2many('res.company.address', 'company_id', 'Email Addresses'),
    }
Company()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

