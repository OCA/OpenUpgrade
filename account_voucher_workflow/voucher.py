
from osv import osv
from osv import fields

class AccountVoucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'state':fields.selection(
            [('draft','Draft'),
             ('proforma','Pro-forma'),
             ('posted','Posted'),
             ('recheck','Waiting for Re-checking'),
             ('cancel','Cancel'),
             ('audit','Audit Complete')
            ], 'State', readonly=True, size=32),
    }
AccountVoucher()
