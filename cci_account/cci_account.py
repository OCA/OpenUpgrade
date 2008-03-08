from osv import fields, osv
import time

class cci_account_message(osv.osv):
    _name = 'cci_account.message'
    _description = 'Notify By Messages'
    _columns = {
        'name' : fields.char('Special Message',size=125,required=True,help='This notification will appear at the bottom of the Invoices when printed.')
    }
cci_account_message()

