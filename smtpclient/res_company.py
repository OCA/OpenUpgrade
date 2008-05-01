from osv import fields,osv
import tools

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

