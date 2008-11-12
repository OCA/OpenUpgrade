# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

from osv import osv, fields
import pooler
import time
import math

from tools import config

class maintenance_maintenance_module(osv.osv):
    _name ="maintenance.maintenance.module"
    _description = "maintenance modules"
    _columns = {
        'name' : fields.char('Name', size=128, required=True),
        'module_name': fields.char('Module Name', size=128, required=True,),
        'version': fields.char('Version', size=64,),
                }
maintenance_maintenance_module()

class maintenance_maintenance(osv.osv):
    _name = "maintenance.maintenance"
    _description = "maintenance"
    _columns = {
    'name' : fields.char('Test Case', size=64),
    'partner_id' : fields.many2one('res.partner','Partner'),
    'partner_invoice_id' : fields.many2one('res.partner.address','Address'),
    'date_from' : fields.date('Date From'),
    'date_to' : fields.date('Date To'),
    'password' : fields.char('password', size=64, invisible=True),
    'module_ids' : fields.many2many('maintenance.maintenance.module','maintenance_module_rel','maintenance_id','module_id',string='Modules'),
    'state' : fields.selection([('draft','Draft'), ('open','Open'), ('cancel','Cancel'), ('done','Done')], 'State', readonly=True),
        }

    _defaults = {
        'date_from':lambda *a: time.strftime('%Y-%m-%d'),
        'password' : lambda obj,cr,uid,context={} : '',
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'maintenance.maintenance'),
        'state': lambda *a: 'draft',
              }

    def check_contract(self, cr, uid, modules, contract):
#        raise osv.except_osv(_('Error !'),_('''Maintenance Contract
#-----------------------------------------------------------
#You do not have a valid maintenance contract ! If you use\
#Open ERP, it's highly suggested to take a maintenance \
#contract. The maintenance program offers you: migrations on \
#new versions, bugfixes guarantee, monthly announces on bugs, \
#security alerts, access to the customer portal.
#* Check the maintenance contract (www.openerp.com)'''))
        external_modules=[]
        maintenance_ids=self.search(cr,uid,[('name','=',contract['name']),('password','=',contract['password']),('date_from','<=',contract['contract_date']),('date_to','>=',contract['contract_date'])],limit=1)
        if maintenance_ids:
            maintenance_obj=self.browse(cr,uid,maintenance_ids)[0]
            name=map(lambda x:x['name'],maintenance_obj.module_ids)
            version=map(lambda x:x['version'],maintenance_obj.module_ids)
            contract_module_list=zip(name,version)
            for module in modules:
                if(module['name'],module['installed_version']) in contract_module_list:
                    continue
                else:
                    external_modules.append(module['name'])
            if external_modules:
                return{
                    'status': 'partial',
                    'modules': external_modules,
                    'message': ''
                    }
            else:
                return{
                    'status': 'ok',
                    'modules': external_modules,
                    'message': ''
                    }
        else:
            return{
                    'status': 'ko',
                    'modules': external_modules,
                    'message': ''
                    }

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_address_id': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['default'])
        return {'value':{'partner_invoice_id': addr['default']}}

maintenance_maintenance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

