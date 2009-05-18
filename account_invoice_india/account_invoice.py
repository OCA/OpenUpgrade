import time
import netsvc
from osv import fields, osv
import ir
import datetime
import calendar
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime
from tools import config

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
                'exise_amt' : fields.float('Exise Amount', digits=(16,2)),
                }
    
account_invoice_line()


class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def _amount_untaxed(self, cr, uid, ids, name, args, context={}):
        id_set=",".join(map(str,ids))
        cr.execute("SELECT s.id,COALESCE(SUM(l.price_unit*l.quantity*(100-l.discount))/100.0,0)::decimal(16,2) AS amount FROM account_invoice s LEFT OUTER JOIN account_invoice_line l ON (s.id=l.invoice_id) WHERE s.id IN ("+id_set+") GROUP BY s.id ")
        res=dict(cr.fetchall())
        return res

    def _amount_tax(self, cr, uid, ids, name, args, context={}):
        id_set=",".join(map(str,ids))
        cr.execute("SELECT s.id,COALESCE(SUM(l.amount),0)::decimal(16,2) AS amount FROM account_invoice s LEFT OUTER JOIN account_invoice_tax l ON (s.id=l.invoice_id) WHERE s.id IN ("+id_set+") GROUP BY s.id ")
        res=dict(cr.fetchall())
        excise_amount=self._excise_amount(cr, uid, ids, name, args, context)
        res[ids[0]]=res[ids[0]]-excise_amount.get(ids[0],0.0)
        return res
    
    def _excise_amount(self, cr, uid, ids, name, args, context={}):
        res={}
        total=0
        child_total=0
        final_total=0
        for id in ids:
            for line in self.browse(cr,uid,id).invoice_line:
                exice=[]
                for tax in line.invoice_line_tax_id:

                    if tax.tax_group == 'excise':
                        exice.append(tax)

                read_data=self.read(cr,uid,id,['name','address_invoice_id','partner_id'])

                for tax in self.pool.get('account.tax').compute(cr, uid, exice, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, read_data.get('address_invoice_id',False)[0], line.product_id, read_data.get('partner_id',False)[0]):
                    total+= tax and tax.get('amount',0.0)
            res[id] = total
        return res

    def _get_type(self, cr, uid, context={}):
        type = context.get('retail_tax', 'tax')
        return type

    def _amount_total(self, cr, uid, ids, name, args, context={}):
        others = self.browse(cr,uid,ids)[0].other_amount
        untax = self._amount_untaxed(cr, uid, ids, name, args, context)
        tax = self._amount_tax(cr, uid, ids, name, args, context)
        excise=self._excise_amount(cr, uid, ids, name, args, context)
        res = {}
        for id in ids:
            res[id] = untax.get(id,0.0) + tax.get(id,0.0) + excise.get(id,0.0) + others
        return res
    
    _columns = {
        'retail_tax': fields.selection([
            ('retail','Retail'),
            ('tax','Tax'),
            ('local_retail','Local Retail'),
            ('service','Service'),
            ],'Invoice', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'latest_date':fields.datetime('Latest Date'),
        'amount_untaxed': fields.function(_amount_untaxed, method=True, digits=(16,2),string='Untaxed', store=True),
        'amount_tax': fields.function(_amount_tax, method=True, string='Tax', store=True),
        'amount_total': fields.function(_amount_total, method=True, string='Total', store=True),
        'excise_amount': fields.function(_excise_amount, method=True,store=True, digits=(16,2),string='Excise'),
        'other_amount' : fields.float('Others', digits=(16,2)),
    }
    _defaults = {
        'retail_tax': _get_type,
        'latest_date': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    
    def onchange_date_invoice(self, cr, uid, ids, date_invoice,latest_date):
        res={'value':{}}
        if not latest_date:
            return res
        if not date_invoice :
            date_invoice = self._defaults["date_invoice"](cr,uid,{})
        data = {}
        data1 = mx.DateTime.strptime(date_invoice,'%Y-%m-%d')
        data2=mx.DateTime.strptime(latest_date,'%Y-%m-%d %H:%M:%S')
        bree = datetime.datetime(data1.year, data1.month, data1.day)
        nat  = datetime.datetime(data2.year, data2.month, data2.day, data2.hour, data2.minute,int(data2.second))
        data3=datetime.datetime(data1.year, data1.month, data1.day,data2.hour, data2.minute,int(data2.second))
        return {'value':{'latest_date':str(data3)}}
    

    def action_number(self, cr, uid, ids, *args):
        cr.execute('SELECT id, retail_tax, type, number, move_id, reference ' \
                'FROM account_invoice ' \
                'WHERE id IN ('+','.join(map(str,ids))+')')
       
        for (id, retail_tax, invtype, number, move_id, reference) in cr.fetchall():
            if not number:

                if retail_tax == 'local_retail':
                    retail_tax = 'tax'
                if invtype in ('out_invoice','out_refund'):
                    number = self.pool.get('ir.sequence').get(cr, uid,'invoice.' + invtype + '.' + retail_tax)
                    if not number:
                        number = self.pool.get('ir.sequence').get(cr, uid,
                            'account.invoice.' + invtype)
                else:
                    number = self.pool.get('ir.sequence').get(cr, uid,
                        'account.invoice.' + invtype)
                    
                if type in ('in_invoice', 'in_refund'):
                    ref = reference
                else:
                    ref = self._convert_ref(cr, uid, number)
                cr.execute('UPDATE account_invoice SET number=%s ' \
                        'WHERE id=%d', (number, id))
                cr.execute('UPDATE account_move_line SET ref=%s ' \
                        'WHERE move_id=%d AND (ref is null OR ref = \'\')',
                        (ref, move_id))
                cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                        'FROM account_move_line ' \
                        'WHERE account_move_line.move_id = %d ' \
                            'AND account_analytic_line.move_id = account_move_line.id',
                            (ref, move_id))
        return True
account_invoice()


class account_tax(osv.osv):
        _inherit = "account.tax"
        _columns = {

            'tax_group': fields.selection([('vat','VAT'),('other','Other'),('excise','Excise')], 'Tax Group', help="If a default tax if given in the partner it only override taxes from account (or product) of the same group."),

    }
account_tax()



class account_invoice_tax(osv.osv):
    _inherit = "account.invoice.tax"

    def compute(self, cr, uid, invoice_id,context={}):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id
        temp=[]
        for line in inv.invoice_line:
            flg=0
            final_total=0.0
            exice_ids=[]
            other_ids=[]
            price_unit = 0.0
            final_price=False
            for tax_line in line.invoice_line_tax_id:
                if tax_line.tax_group == 'excise':
                    exice_ids.append(tax_line)
                else:
                    other_ids.append(tax_line)
            if len(exice_ids)>0:
                for tax in tax_obj.compute(cr, uid, exice_ids, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id):
                    val={}
                    val['invoice_id'] = inv.id
                    val['name'] = tax['name']
                    val['amount'] = cur_obj.round(cr, uid, cur, tax['amount'])
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = tax['price_unit'] * line['quantity']
                    if inv.type in ('out_invoice','in_invoice'):
                        val['base_code_id'] = tax['base_code_id']
                        val['tax_code_id'] = tax['tax_code_id']
                        val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice})
                        val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice})
                        val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    else:
                        val['base_code_id'] = tax['ref_base_code_id']
                        val['tax_code_id'] = tax['ref_tax_code_id']
                        val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice})
                        val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice})
                        val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                    if not key in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
                        tax_grouped[key]['base_amount'] += val['base_amount']
                        tax_grouped[key]['tax_amount'] += val['tax_amount']
                    final_total+= val and val.get('tax_amount',0.0)
                    flg=1
            final_price=(final_total+line.price_subtotal)/line.quantity
            if final_price:
                self.pool.get('account.invoice.line').write(cr, uid, line.id,{'exise_amt':final_price})
            if len(other_ids)>0:
                if flg:
                    price_unit =  final_price and final_price
                else:
                    price_unit =   (line.price_unit* (1-(line.discount or 0.0)/100.0))
                for tax in tax_obj.compute(cr, uid, other_ids, price_unit, line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id):
                    val={}
                    val['invoice_id'] = inv.id
                    val['name'] = tax['name']
                    val['amount'] = cur_obj.round(cr, uid, cur, tax['amount'])
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = tax['price_unit'] * line['quantity']
                    if inv.type in ('out_invoice','in_invoice'):
                        val['base_code_id'] = tax['base_code_id']
                        val['tax_code_id'] = tax['tax_code_id']
                        val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice})
                        val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice})
                        val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    else:
                        val['base_code_id'] = tax['ref_base_code_id']
                        val['tax_code_id'] = tax['ref_tax_code_id']
                        val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice})
                        val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice})
                        val['account_id'] = tax['account_paid_id'] or line.account_id.id

                    key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                    if not key in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
                        tax_grouped[key]['base_amount'] += val['base_amount']
                        tax_grouped[key]['tax_amount'] += val['tax_amount']
        return tax_grouped
account_invoice_tax()








    
