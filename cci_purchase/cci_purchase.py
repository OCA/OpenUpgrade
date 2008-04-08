##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

import netsvc
import time
from osv import fields, osv

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _decription = 'purchase order'
    def wkf_temp_order(self ,cr, uid, ids,context={}):
        print "wkf_temp_order::::::::"
        super(purchase_order,self).wkf_confirm_order(cr, uid, ids, context)
        return True

    def wkf_confirm_order(self, cr, uid, ids, context={}):
        for po in self.browse(cr, uid, ids):
            if po.amount_total > 10000:
                self.write(cr, uid, [po.id], {'state' : 'temp', 'validator' : uid})
            else:
                super(purchase_order,self).wkf_confirm_order(cr, uid, ids, context)
        return True
    _columns = {
        'state': fields.selection([('draft', 'Request for Quotation'), ('wait', 'Waiting'), ('pass', 'pass'), ('confirmed', 'Confirmed'),('temp','Temp'), ('approved', 'Approved'),('except_picking', 'Shipping Exception'), ('except_invoice', 'Invoice Exception'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Order State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
                }
purchase_order()
