from osv import fields, osv
import time

class cci_account_message(osv.osv):
    _name = 'cci_account.message'
    _description = 'Notify By Messages'
    _columns = {
        'title' :  fields.char('Title',size=64,required=True),
        'name' : fields.char('Special Message',size=125,required=True,help='This notification will appear at the bottom of the Invoices when printed.')
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
