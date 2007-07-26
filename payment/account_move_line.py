##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields
from osv import osv

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def amount_to_pay(self, cr, uid, ids, name, arg={}, context={}):
        """ Return the amount still to pay regarding all the payemnt orders (excepting cancelled orders)"""
	if not ids:
	    return {}
        cr.execute("SELECT id,debit - (select id,coalesce(sum(amount),0) from payment_line pl inner join payment_order po on (pl.order = po.id)where move_line = ml.id and po.state != 'cancel') as amount from account_move_line ml where debit > 0 and id in %s;"% (",".join(map(str,ids))))
        return dic(cr.fetchall())
    
    _columns = {
        'amount_to_pay' : fields.function(amount_to_pay, method=True, type='float', string='Amount to pay'),
                }
account_move_line()
