import time

#import osv;
from osv import osv
from osv import fields


#myloan_loantype class is created by dhaval patel and it is used as loan type for a loan
#for e.g. Home loan, Vehical Loan, Personal Loan, Business loan


class account_loan_loantype(osv.osv):
    _name = "account.loan.loantype"
    _description = "account loan type "
    _columns = {
                'name' : fields.char('Type Name', size=32,required=True),
                #'notes': fields.text('Description'),
                #'interestrate' : fields.float('Interest Rate'),
                'prooftypes' : fields.many2many('account.loan.proof.type', 'loantype_prooftype_rel', 'order_line_id', 'tax_id', 'Taxes'),
                #'active': fields.boolean('Active'),
                'calculation':fields.selection(
                   [('simple','Simple'),('compute','Compound')],'Calculation Method'),
                'interestversion_ids' : fields.one2many('account.loan.loantype.interestversion','loantype_id','Interest Versions'),
    }
#end class
account_loan_loantype();

class account_loan_loantype_interestversion(osv.osv):
    _name='account.loan.loantype.interestversion'
    _columns={
        'name':fields.char('Name',size=32,required=True),
        'loantype_id':fields.many2one('account.loan.loantype','Loan Type'),
        'start_date':fields.date('Start Date'),
        'end_date':fields.date('End Date'),
        'active':fields.boolean('Active'),
        'interestversionline_ids':fields.one2many('account.loan.loantype.interestversionline','interestversion_id','Current Interest Version'),
        'sequence':fields.integer('Sequence',size=32),
    }
    _order = 'sequence'
    _defaults = {
        'active': lambda *a: True,
    }
account_loan_loantype_interestversion();

class account_loan_loantype_interestversionline(osv.osv):
    _name='account.loan.loantype.interestversionline';
    _columns={
        'name':fields.char('Interest ID',size=32,required=True),
        'interestversion_id':fields.many2one('account.loan.loantype.interestversion','Loan Interest Id'),
        'min_month' : fields.integer('Minimum Month',size=32),
        'max_month' : fields.integer('Maximum Month',size=32),
        'min_amount': fields.float('Minimum Amount', digits=(10,2)),
        'max_amount': fields.float('Maximum Amount', digits=(10,2)),
        'rate':fields.float('Rate',digits=(10,2)),
        'sequence':fields.integer('Sequence',size=32),
    }
    _order = 'sequence'
account_loan_loantype_interestversionline();

