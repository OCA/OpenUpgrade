from osv import fields,osv
import tools

class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {        
        'addresses': fields.one2many('res.company.address', 'name', 'Email Addresses'),
    }
    
res_company()
class res_company_address(osv.osv):
    _name = "res.company.address"
    _columns = {        
        'name': fields.char('Email Address', size=64,required=True),
        'type' : fields.selection([("default", "Default"),("inoice", "Invoice"),("sale","Sale"),("delivery","Delivery")], "Address Type",required=True)
    }
res_company_address()