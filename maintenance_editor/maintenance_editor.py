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
import uuid
import addons

from tools import config
import mx.DateTime

class maintenance_maintenance_module(osv.osv):
    _name ="maintenance.maintenance.module"
    _description = "maintenance modules"
    _columns = {
        'name' : fields.char('Name', size=128, required=True),
        'version': fields.char('Version', size=64,),
    }
maintenance_maintenance_module()

class maintenance_maintenance(osv.osv):
    _name = "maintenance.maintenance"
    _description = "maintenance"

    def _contract_date(self, cr, uid, ids):
        for contract in self.browse(cr, uid, ids):
            cr.execute("""
                        SELECT count(1) 
                          FROM maintenance_maintenance 
                        WHERE (    (%(date_from)s BETWEEN date_from AND date_to)
                                OR (%(date_to)s BETWEEN date_from AND date_to)
                                OR (%(date_from)s < date_from AND %(date_to)s > date_to)
                               )
                           AND partner_id = %(partner)s 
                           AND id <> %(id)s
                           AND state = %(state)s
                        """, { 
                         "date_from": contract.date_from,
                         "date_to": contract.date_to,
                         "partner": contract.partner_id.id,
                         "id": contract.id,
                         "state": "open"
                        })
            if cr.fetchone()[0]:
                return False
        return True

    _columns = {
        'name' : fields.char('Contract ID', size=64, required=True),
        'partner_id' : fields.many2one('res.partner','Partner', required=True),
        'partner_invoice_id' : fields.many2one('res.partner.address','Address'),
        'date_from' : fields.date('Date From', required=True),
        'date_to' : fields.date('Date To', required=True),
        'password' : fields.char('Password', size=64, invisible=True, required=True),
        'module_ids' : fields.many2many('maintenance.maintenance.module','maintenance_module_rel','maintenance_id','module_id',string='Modules'),
        'state' : fields.selection([('draft','Draft'), ('open','Open'), ('cancel','Cancel'), ('done','Done')], 'State', readonly=True),
    }

    _defaults = {
        'date_from':lambda *a: time.strftime('%Y-%m-%d'),
        'password' : lambda *a : str(uuid.uuid4()).split('-')[-1],
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'maintenance.maintenance'),
        'state': lambda *a: 'draft',
    }

    _sql_constraints = [
        ("check_dates", "CHECK (date_from < date_to)", 'The "from" date must not be after the "to" date.'),
    ]
    _constraints = [
        (_contract_date, 'You can not have 2 contracts that overlaps !', ['date_from','date_to']),
    ]

    def check_contract(self, cr, uid, modules, contract):
        external_modules = []
        contract_module_list = []
        date_from = date_to = False
        maintenance_ids=self.search(cr,uid,
                                    [('name','=',contract['name']),
                                     ('password','=',contract['password']),
                                     ('date_from','<=',mx.DateTime.today()),
                                     ('date_to','>=',mx.DateTime.today())
                                    ],limit=1)
        if maintenance_ids:
            maintenance_obj = self.browse(cr,uid,maintenance_ids)[0]
            date_from = maintenance_obj.date_from
            date_to = maintenance_obj.date_to
            contract_module_list = map(lambda x:(x['name'], x['version']),maintenance_obj.module_ids)
            for module in modules:
                if (module['name'],module['installed_version']) not in contract_module_list:
                    external_modules.append(module['name'])
        return { 
            'id': (maintenance_ids and maintenance_ids[0] or 0),
            'status': (maintenance_ids and ('full', 'partial')[bool(external_modules)] or 'none'),
            'external_modules': external_modules,
            'modules_with_contract' : contract_module_list,
            'message': '',
            'date_from': date_from,
            'date_to': date_to,
        }

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_address_id': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['default'])
        return {'value':{'partner_invoice_id': addr['default']}}

    def onchange_date_from(self, cr, uid, ids, date_from):
        if not date_from:
            return {'value:':{'date_to':False}}
        return { 
            'value': { 
                'date_to' : (mx.DateTime.strptime(date_from, '%Y-%m-%d') + mx.DateTime.RelativeDate(years=1)).strftime("%Y-%m-%d") 
            }
        }
    
    def retrieve_updates(self, cr, uid, ids):
        res = {}
        toload = ids
        if isinstance(ids, (int, long)):
            toload = [ids]
        for c in self.browse(cr, uid, toload):
            res[str(c.id)] = {}
            for m in c.module_ids:
                res[str(c.id)][m.name] = addons.get_module_as_zip(m.name, b64enc=True)

        if isinstance(ids, (int, long)):
            return res[str(ids)]
        return res

maintenance_maintenance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

