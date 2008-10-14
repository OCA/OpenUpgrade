# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: make_invoice.py 1070 2005-07-29 12:41:24Z nicoe $
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

import wizard
import pooler
from osv import fields, osv

def _reg_check(self, cr, uid, data, context={}):
    pool_obj = pooler.get_pool(cr.dbname)
    obj_reg = pool_obj.get('event.registration')
    reg_ids = obj_reg.search(cr,uid,[('check_mode','=',True)])
    data_temp = obj_reg.browse(cr,uid,reg_ids)
    ids_case = []
    for i in data_temp:
        if not i.check_ids:
            ids_case.append(i.case_id)
    data['form']['ids_case'] = ids_case
    return {}

class missing_check_reg(wizard.interface):
    def _open_reg(self, cr, uid, data, context):
        pool_obj = pooler.get_pool(cr.dbname)
        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','event_registration_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
        return {
            'domain': "[('case_id','in', ["+','.join(map(str,data['form']['ids_case']))+"])]",
            'name': 'Registration',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'event.registration',
            'views': [(False,'tree'),(resource_id,'form')],
            'type': 'ir.actions.act_window'
        }
    states = {
        'init' : {
            'actions' : [_reg_check],
            'result' : {'type':'action', 'action':_open_reg, 'state':'end'}
        },
    }
missing_check_reg("cci_event.reg_checks")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

