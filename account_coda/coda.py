import time
from osv import osv,fields

class account_coda(osv.osv):
    _name = "account.coda"
    _description = "coda for an Account"
    _columns = {
        'name': fields.binary('Coda file', readonly=True),
        'statement_ids': fields.one2many('account.bank.statement','Bank Statement','Generated Bank Statement', readonly=True),
        'note': fields.text('Import log', readonly=True),
        'journal_id': fields.many2one('account.journal','Bank Journal', readonly=True,select=True),
        'date': fields.date('Import Date', readonly=True,select=True),
        'user_id': fields.many2one('res.users','User', readonly=True, select=True),
    }
account_coda()

class account_bank_statement(osv.osv):
    _inherit = "account.bank.statement"
    _columns = {
        'coda_id':fields.many2one('account.coda','Coda'),
    }
account_bank_statement()

