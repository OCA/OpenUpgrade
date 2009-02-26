from osv import fields, osv

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'vat_no' : fields.char('VAT Number', size=256),
        'cst_no' : fields.char('CST Number', size=256),
        'pan_no' : fields.char('PAN Number', size=256),
        'ser_tax': fields.char('Service Tax Number', size=256),
        'excise' : fields.char('Exices Number', size=256),
        'range'  : fields.char('Range', size=256),
        'div'    : fields.char('Division', size=256),
    }
res_partner()
