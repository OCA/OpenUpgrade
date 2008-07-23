# -*- encoding: utf-8 -*-
##################################################################################
#
# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com) All Rights Reserved.
#
# $Id: hr.py 4656 2006-11-24 09:58:42Z Cyp $
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

from mx import DateTime
import time
import pooler
import netsvc
from osv import fields, osv

def _employee_get(obj,cr,uid,context={}):
    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
    if ids:
        return ids[0]
    return False

class hr_holidays(osv.osv):
    _name = "hr.holidays"
    _inherit = 'hr.holidays'
    _description = "Holidays"
    _columns = {
        'name' : fields.char('Description', required=True, readonly=True, size=64, states={'draft':[('readonly',False)]}),
        'state': fields.selection([('draft', 'draft'), ('confirm', 'Confirmed'), ('refuse', 'Refused'), ('validate', 'Validate'), ('cancel', 'Cancel')], 'State', readonly=True),
        'date_from' : fields.datetime('Vacation start day', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_to' : fields.datetime('Vacation end day', readonly=True, states={'draft':[('readonly',False)]}),
        'holiday_status' : fields.many2one("hr.holidays.status", "Holiday's Status", readonly=True, states={'draft':[('readonly',False)]}),
        'employee_id' : fields.many2one('hr.employee', 'Employee', select=True, invisible=False, readonly=True, states={'draft':[('readonly',False)]}),
        'user_id':fields.many2one('res.users', 'Employee_id', states={'draft':[('readonly',False)]}, relate=True, select=True, readonly=True),
        'manager_id' : fields.many2one('hr.employee', 'Holiday manager', invisible=False, readonly=True),
        'notes' : fields.text('Notes'),
    }
    _defaults = {
        'employee_id' : _employee_get ,
        'state' : lambda *a: 'draft',
        'user_id': lambda obj, cr, uid, context: uid
    }
    _order = 'date_from desc'
    def set_to_draft(self, cr, uid, ids, *args):
        #for exp in self.browse(cr, uid, ids):
        self.write(cr, uid, ids, {
            'state':'draft'
        })
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_create(uid, 'hr.holidays', ids[0], cr)
        return True

    def holidays_validate(self, cr, uid, ids, *args):
        #for exp in self.browse(cr, uid, ids):
        ids2 = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
        self.write(cr, uid, ids, {
            'state':'validate',
            'manager_id':ids2[0]
        })
        return True

    def holidays_confirm(self, cr, uid, ids, *args):
        #for exp in self.browse(cr, uid, ids):
        self.write(cr, uid, ids, {
            'state':'confirm'
        })
        return True

    def holidays_refuse(self, cr, uid, ids, *args):
        #for exp in self.browse(cr, uid, ids):
        ids2 = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
        self.write(cr, uid, ids, {
            'state':'refuse',
            'manager_id':ids2[0]
        })
        return True

    def holidays_cancel(self, cr, uid, ids, *args):
        #for exp in self.browse(cr, uid, ids):
        self.write(cr, uid, ids, {
            'state':'cancel'
            })
        return True

    def holidays_draft(self, cr, uid, ids, *args):
        #for exp in self.browse(cr, uid, ids):
        self.write(cr, uid, ids, {
            'state':'draft'
        })
        return True

hr_holidays()

class hr_holidays_status(osv.osv):
    _name = "hr.holidays.status"
    _inherit = 'hr.holidays.status'
    _description = "Holidays Status"
    _columns = {
        'color_name' : fields.selection([('red', 'Red'), ('green', 'Green'), ('blue','Blue'), ('yellow', 'Yellow'), ('magenta', 'Magenta'),('cyan', 'Cyan'),('black', 'Black'),('pink', 'Pink'),('brown', 'Brown'),('indigo', 'Indigo'),('lightcoral', 'Light Coral'),('lightsteelblue', 'Light Steel Blue')],'Color of the status', required=True),
    }
    _defaults = {
        'color_name': lambda *args: 'red',
    }
hr_holidays_status()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

