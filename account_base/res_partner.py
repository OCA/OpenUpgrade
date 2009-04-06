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

# Set Accounts Detail with Company partner wizard

class wizard_account_base_setup(osv.osv_memory):
    """
    Insert Information for a company.
    Wizards ask for:
        * A Company with its partner
        * Fill All Related Detail for Exice Invoice. 
    """
    _name='wizard.account.base.setup'

    _columns = {
        'company_id':fields.many2one('res.company','Company',required=True),
        'partner_id':fields.many2one('res.partner','Partner'),
        'vat_no' : fields.char('VAT Number', size=256),
        'cst_no' : fields.char('CST Number', size=256),
        'pan_no' : fields.char('PAN Number', size=256),
        'ser_tax': fields.char('Service Tax Number', size=256),
        'excise' : fields.char('Exices Number', size=256),
        'range'  : fields.char('Range', size=256),
        'div'    : fields.char('Division', size=256),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr,uid,[uid],c)[0].company_id.id,
        'partner_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr,uid,[uid],c)[0].company_id.partner_id.id,
    }

        
    def action_create(self, cr, uid, ids, context=None):
        wiz_data = self.pool.get('wizard.account.base.setup').read(cr,uid,ids,['partner_id','vat_no','cst_no','pan_no','sr_tax','excise','range','div'])[0]
        self.pool.get('res.partner').write(cr, uid, [ wiz_data['partner_id'] ], {
                'vat_no':wiz_data['vat_no'],
                'cst_no':wiz_data['cst_no'],
                'pan_no':wiz_data['pan_no'],
                'ser_tax':wiz_data['sr_tax'],
                'excise':wiz_data['excise'],
                'range':wiz_data['range'],
                'div':wiz_data['div'],
            })
        
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

    def action_cancel(self,cr,uid,ids,conect=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

wizard_account_base_setup()   


