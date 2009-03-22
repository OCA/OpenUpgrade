import time
from osv import osv
from osv import fields

class account_loan_proof_type(osv.osv):
    _name="account.loan.proof.type"
    _columns={
          'name'   : fields.char('Proof Type Name',size=64,required=True),
          "shortcut":fields.char("Shortcut",size=32,required=True),
          }
#End Class
account_loan_proof_type();

def _account_loan_proof_type_get(self,cr,uid,context={}):
    obj = self.pool.get('account.loan.proof.type')
    ids = obj.search(cr, uid,[('name','ilike','')])
    res = obj.read(cr, uid, ids, ['shortcut','name'], context)
    return [(r['name'], r['name']) for r in res]

class account_loan_proof(osv.osv):
    _name='account.loan.proof'
    _columns = {
           'name': fields.char('Proof name',size=256,required=True),
           'loan_id': fields.many2one('account.loan', 'Loan '),
           'note':fields.text('Proof Note'),
           'document':fields.binary('Proof Document'),
           'type': fields.selection(_account_loan_proof_type_get
                      ,'Type',select=True),
           'state': fields.selection([
           ('draft','Draft'),
           ('apply','Under Varification'),
           ('done','Varified'),
           ('cancel','Cancel')
          ],'State', readonly=True, select=True),
      }
    _defaults = {
                     'state': lambda *a: 'draft',
                 }
    def apply_varification(self, cr, uid, ids,context = {}):
        self.pool.get('account.loan.proof').write(cr,uid,ids,{'state':'apply'})
        return True
    #end method
    def proof_varified(self,cr,uid,ids,context = {}):
        self.pool.get('account.loan.proof').write(cr,uid,ids,{'state':'done'})
        return True
    #end Method
    def proof_canceled(self,cr,uid,ids,context = {}):
        self.pool.get('account.loan.proof').write(cr,uid,ids,{'state':'cancel'})
        return True
    #end Method

#End Class
account_loan_proof();