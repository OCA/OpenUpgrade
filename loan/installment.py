

import time

#import osv;

from osv import osv
from osv import fields

class account_loan_installment(osv.osv):
    _name = 'account.loan.installment'
    _columns = {
        #'installment_id':fields.char('Installment Id', size=32, required=False),
        'name': fields.char('Description',size=64 ),
        'loan_id': fields.many2one('account.loan', 'Loan'),
        'capital': fields.float('Installment'),
        'interest': fields.float('Interest'),
        'total': fields.float('Installment'),
        'cheque_id' : fields.many2one('account.loan.bank.cheque','Bank Cheque')
    }
#end class
account_loan_installment();

class loan_installment_period(osv.osv):
    _name = 'loan.installment.period'
    _columns ={
               'name':fields.char('Period Name', size=64, required=True),
               'period':fields.integer('Loan Period', required = True),
               }
#end class
loan_installment_period();