
import time
import netsvc
from osv import fields, osv

class AccountJournal(osv.osv):
    _inherit = "account.journal"
    _columns = {
        'analytic_journal_id': fields.many2one('account.analytic.journal', 'Analytic Journal')
    }
AccountJournal()

class AccountLine(osv.osv):
    _inherit = "account.move.line"
    _description = "Entry lines"
    _columns={
        'analytic_account':fields.many2one('account.analytic.account','Analytic Account'),
    }

    def create(self, cr, uid, vals, context=None, check=True):
        analytic = self.pool.get('account.analytic.line')
        amount = 0
        if vals['debit'] > 0:
            amount =  vals['debit']
        elif vals['credit'] > 0:
            amount = -1 * vals['credit']
        
        id = super(AccountLine, self).create(cr, uid, vals, context, check)
        
        move = self.browse(cr, uid, id)
        
        move_id = move.move_id
        journal_id = move.journal_id
        
        if vals.get('analytic_account',False):
            res = {
                'name' : vals['name'],
                'amount' : amount,
                'general_account_id': vals['account_id'],
                'move_id':move_id.id,
                'journal_id':journal_id.analytic_journal_id.id,
                'account_id':vals['analytic_account'],
                'unit_amount':1
            }
            analytic.create(cr, uid, res)
    
        return id
AccountLine()