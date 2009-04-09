import time
from osv import osv
from osv import fields
import pooler
import ir

class account_loan_bank_cheque(osv.osv):

    _name='account.loan.bank.cheque'
    _description='Bank Account Cheque'
    _rec_name = 'code'
    _columns={
        'loan_id':fields.many2one('account.loan','Loan', required=False),
        'code':fields.char('Code', size=32, required=True),
        'name':fields.char('Name', size=32,required=True),
        'partner_id':fields.many2one('res.partner', 'Customer', required=True),
        'loan_bank_id':fields.many2one('res.bank','Bank', required=True),

        'loan':fields.float('Loan Amount', size=32),
        'interest':fields.float('Interest Amount', size=32),

        'cheque_amount':fields.float('Cheque Amount', size=32, required=True),
        'account_id':fields.many2one('account.account', 'General Account', required=True, select=True),
        'state':fields.selection([
                ('draft','Draft'),
                ('posted','Posted'),
                ('clear','Clear'),
                ('return','Return'),
                ('cancel','Cancel'),
                ('done','Done')],'State', readonly=True, select=True),
        'date':fields.date('Date', required=True),
        'clear_date':fields.date('Cheque Clearing Date', required=False, readonly=True),
        'return_date':fields.date('Cheque Return Date', required=False, readonly=True),
        'note':fields.text('Notes'),
        'cheque_id' :fields.one2many('account.loan.installment','cheque_id','Installments'),
    }
    _defaults={
       'state':lambda *a:'draft',
       'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def onchange_bank_id(self, cr, uid, ids, part):
        val={'loan_bank_id': False,'account_id':False,'loan_id':False}
        if not part:
            return {'value':val}
        else:
            bank_ids=self.pool.get('account.bank').search(cr,uid,[('partner_id','=',part)])
            loan_ids=self.pool.get('account.loan').search(cr,uid,[('partner_id','=',part)])
            if loan_ids.__len__()>0:
                val['loan_id']=loan_ids[0];
            if bank_ids.__len__()>0:
                acc_ids=self.pool.get('account.bank.account').search(cr,uid,[('bank_id','=',bank_ids[0])])
                if acc_ids:
                    val['loan_bank_id']=bank_ids[0];
                    val['account_id']=acc_ids[0];
                    return {'value':val}
                else:
                    val['loan_bank_id']=bank_ids[0];
                    return {'value':val}
            else:
                return {'value':val}
        #end if
    #end def

    def cheque_clear(self, cr, uid, ids, context={}):

        res = False
        invoices = {}
        invoice_ids = []

        def make_invoice(cheque):
            a = cheque.partner_id.property_account_receivable.id
            b = cheque.partner_id.property_account_payable.id
            print cheque
            if cheque.partner_id and cheque.partner_id.property_payment_term:
                pay_term = cheque.partner_id.property_payment_term.id
            else:
                pay_term = False

            create_ids=[]
            inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': cheque.name,
                    'account_id': a,#source
                    'price_unit': cheque.loan,
                    'quantity': 1,
                    'discount': False,
                    'uos_id': False,
                    'product_id': False,
                    'invoice_line_tax_id': False,
                    'note':False,
            })
            create_ids.append(inv_id)

            inv_id1 = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': cheque.name,
                    'account_id': 60,#source
                    'price_unit': cheque.interest,
                    'quantity': 1,
                    'discount': False,
                    'uos_id': False,
                    'product_id': False,
                    'invoice_line_tax_id': False,
                    'note':False,
            })
            create_ids.append(inv_id1)

            inv = {
                'name': cheque.name,
                'origin': cheque.name,
                'type': 'out_invoice',
                'reference': "P%dSO%d"%(cheque.partner_id.id,cheque.id),
                'account_id': b,#destination
                'partner_id': cheque.partner_id.id,
                'address_invoice_id': False,
                'address_contact_id': False,
                'project_id': cheque.loan_bank_id.id,
                'invoice_line': [(6,0,create_ids)],
                'currency_id' : cheque.account_id.currency_id.id,
                'comment': "",#order.note,
                'payment_term': pay_term,
            }
            print inv['invoice_line']

            inv_obj = self.pool.get('account.invoice')
            inv_id = inv_obj.create(cr, uid, inv)

            inv_obj.button_compute(cr, uid, [inv_id])
            return inv_id

        for o in self.pool.get('account.loan.bank.cheque').browse(cr,uid,ids):
            self.write(cr, uid, [o.id], {'clear_date': time.strftime('%Y-%m-%d')})
            res = make_invoice(o)

            print res

        return res
    #end def

    def cheque_return(self, cr, uid, ids, context={}):
        for o in self.pool.get('account.loan.bank.cheque').browse(cr,uid,ids):
            self.write(cr, uid, [o.id], {'return_date': time.strftime('%Y-%m-%d')})
#end def

#end class
account_loan_bank_cheque()


