# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import netsvc
from osv import fields, osv

class mrp_procurement(osv.osv):
    _inherit = "mrp.procurement"
    def action_po_assign(self,cr, uid, ids):
        res = super(mrp_procurement,self).action_po_assign(cr, uid, ids)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', res, 'purchase_confirm', cr)
        wf_service.trg_validate(uid, 'purchase.order', res, 'purchase_approve', cr)
        return res

mrp_procurement()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

