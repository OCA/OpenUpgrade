from osv import fields, osv
import time

class cci_account_message(osv.osv):
    _name = 'cci_account.message'
    _description = 'Notify By Messages'
    _columns = {
        'name' :  fields.char('Title',size=64,required=True),
        'title' : fields.text('Special Message',size=125,required=True,help='This notification will appear at the bottom of the Invoices when printed.',translate=True)
    }

cci_account_message()

class account_move_line(osv.osv):

    def search(self, cr, user, args, offset=0, limit=None, order=None,
            context=None, count=False):
        # will check if the partner/account exists in statement lines if not then display all partner's account.move.line
        for item in args:
            if (item[0] in ('partner_id','account_id')) and (not item[2]):
                args.pop(args.index(item))

        return super(account_move_line,self).search(cr, user, args, offset, limit, order,
            context, count)

    _inherit = "account.move.line"
    _description = "account.move.line"

account_move_line()

class account_invoice(osv.osv):

    _inherit = 'account.invoice'
    _columns = {
        'internal_note': fields.text('Internal Note'),
            }

    def action_move_create(self, cr, uid, ids, context=None):
        flag = False
        data_invoice = self.browse(cr,uid,ids[0])
        for line in data_invoice.invoice_line:
            if not line.account_analytic_id:
                flag = True
        if flag:
            raise osv.except_osv('Error!','Invoice line should have Analytic Account')
        return super(account_invoice, self).action_move_create(cr, uid, ids, context)

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,date_invoice=False, payment_term=False, partner_bank_id=False):
        if partner_id:
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            if data_partner.alert_others:
                raise osv.except_osv('Error!',data_partner.alert_explanation or 'Partner is not valid')
        return super(account_invoice,self).onchange_partner_id( cr, uid, ids, type, partner_id,date_invoice, payment_term, partner_bank_id)

    def create(self, cr, uid, vals, *args, **kwargs):
        product_ids = []
        flag = False
        if 'abstract_line_ids' in vals:
            for lines in vals['abstract_line_ids']:
                if lines[2]['product_id']:
                    product_ids.append(lines[2]['product_id'])
        if product_ids:
            data_product = self.pool.get('product.product').browse(cr,uid,product_ids)
            for product in data_product:
                if product.membership:
                    flag = True
        if vals['partner_id']:
            data_partner = self.pool.get('res.partner').browse(cr,uid,vals['partner_id'])
            if data_partner.alert_membership and flag:
                raise osv.except_osv('Error!',data_partner.alert_explanation or 'Partner is not valid')
        return super(account_invoice,self).create(cr, uid, vals, *args, **kwargs)

    def write(self, cr, uid, ids,vals, *args, **kwargs):
        product_ids = []
        a = super(account_invoice,self).write(cr, uid, ids,vals, *args, **kwargs)
        flag = False
        data_inv = self.browse(cr,uid,ids[0])
        for lines in data_inv.abstract_line_ids:
            if lines.product_id:
                product_ids.append(lines.product_id.id)
        if product_ids:
            data_product = self.pool.get('product.product').browse(cr,uid,product_ids)
            for product in data_product:
                if product.membership:
                    flag = True
        if data_inv.partner_id.alert_membership and flag:
            raise osv.except_osv('Error!',data_inv.partner_id.alert_explanation or 'Partner is not valid')
        return a

account_invoice()