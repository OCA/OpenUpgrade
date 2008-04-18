from osv import fields, osv
import time

class cci_account_message(osv.osv):
    _name = 'cci_account.message'
    _description = 'Notify By Messages'
    _columns = {
        'name' : fields.char('Special Message',size=125,required=True,help='This notification will appear at the bottom of the Invoices when printed.')
    }
cci_account_message()

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _description = "account.move.line"

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
#        if not args:
#            args=[]
#        if not context:
#            context={}
        # will check if the partner exists in statement lines if not then display all partner's account.move.line
        if not context['partner_id']:
            args.pop(0)
            if not context['account_id']:
                args=[]
                args.append(['reconcile_id', '=', False])
                args.append(['state', '=', 'valid'])
        else:
            if not context['account_id']:
                args.pop(2)
            else:
                return super(account_move_line,self).name_search(cr, user, name, args, operator, context, limit)
        args=args[:]
        if name:
            args += [(self._rec_name,operator,name)]
        ids = self.search(cr, user, args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

account_move_line()
