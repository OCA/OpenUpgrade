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
import os

from tools import config
from tools.parse_version import parse_version
from tools.misc import file_open, debug
import mx.DateTime

import release


import wizard
import pooler

class maintenance_maintenance_module_refresh_wizard(wizard.interface):
    def init(self, cr, uid, data, context):
        pooler.get_pool(cr.dbname).get('maintenance.maintenance.module').refresh(cr, uid)
        raise osv.except_osv(_('Refresh'), _('List refreshed successfully'))
        return {}

    states = {
        'init': {
            'actions': [init],
            'result': {'type': 'state', 'state': 'end'}
        }
    }
maintenance_maintenance_module_refresh_wizard("maintenance.maintenance.module.refresh")


class maintenance_maintenance_module(osv.osv):
    
    __root_path = os.path.join(config['root_path'], 'maintenance', 'addons')

    def _get_module_path(self, cr, uid, ids, name, args, context=None):
        result = {}
        for module in self.browse(cr, uid, ids, context):
            result[module.id] = os.path.join(self.__root_path, module.name)
        return result
    
    
    _name ="maintenance.maintenance.module"
    _description = "maintenance modules"
    _columns = {
        'name' : fields.char('Name', size=128, required=True, readonly=True),
        'version': fields.char('Version', size=64, readonly=True),
        'certificate': fields.char('Certificate Code', size=42, 
                                  required=True, readonly=True),
        'path': fields.function(_get_module_path, method=True, string='Path',
                                type='char', size=512, readonly=True),
    }
    

    def refresh(self, cr, uid):
        def get_version(terp):
            return "%s.%s" % (release.major_version, terp['version'])

        def get_terp(moddir):
            try:
                terp = file_open(os.path.join(moddir, '__terp__.py'))
                try:
                    return eval(terp.read())
                finally:
                    terp.close()
            except IOError:
                return None

        if not os.path.exists(self.__root_path):
            os.makedirs(self.__root_path)

        ids = self.search(cr, uid, [])
        names = []
        for module in self.browse(cr, uid, ids):
            names.append(module.name)
            terp = get_terp(module.path)
            if terp:
                module.write({'version': get_version(terp)}) # certificate is not updated

        for element in os.listdir(self.__root_path):
            if element in names:
                continue
            
            element_dir = os.path.join(self.__root_path, element)
            if not os.path.isdir(element_dir):
                continue

            terp = get_terp(element_dir)
            if terp and 'certificate' in terp:
                self.create(cr, uid, {'name': element, 
                                      'version': get_version(terp), 
                                      'certificate': terp['certificate']}
                )

        return True

    def init(self, cr):
        self.refresh(cr, 1)
            
maintenance_maintenance_module()


class maintenance_contract_type(osv.osv):
    _name = "maintenance.contract.type"

    _columns = {
        'name': fields.char('Name', size=32, required=True, select=1),
        'product_id': fields.many2one('product.product', 'Product'),
        'crm_case_section_id': fields.many2one('crm.case.section', 'CRM Case Section', required=True),
        'crm_case_categ_id': fields.many2one('crm.case.categ', 'CRM Case Category', required=True, 
            domain="[('section_id', '=', crm_case_section_id)]"),

    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the maintenance contract type must be unique !')
    ]
    
maintenance_contract_type()


class maintenance_maintenance(osv.osv):
    _name = "maintenance.maintenance"
    _description = "maintenance contract"

    def _contract_date(self, cr, uid, ids):
        for contract in self.browse(cr, uid, ids):
            cr.execute("""
                        SELECT count(1) 
                          FROM maintenance_maintenance 
                         WHERE (   (%(date_from)s BETWEEN date_from AND date_to)
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
        'note': fields.text('Note'),
        'type_id': fields.many2one('maintenance.contract.type', 'Contract Type', required=True),
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
        (_contract_date, 'You can not have 2 contracts (for the same partner) that overlaps !', ['partner_id', 'date_from','date_to']),
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
            contract_module_list = map(lambda x:(x['name'], x['version']), maintenance_obj.module_ids)
            for module in modules:
                if (module['name'], module['installed_version']) not in contract_module_list:
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

    def __for_each_module(self, cr, uid, ids, modules, callback):
        res = {}
        toload = ids
        if isinstance(ids, (int, long)):
            toload = [ids]
        for c in self.browse(cr, uid, toload):
            res[str(c.id)] = {}
            for m in c.module_ids:
                if (m.name not in modules) or parse_version(modules[m.name]) < parse_version(m.version):
                    res[str(c.id)][m.name] = callback(m)

        if isinstance(ids, (int, long)):
            return res[str(ids)]
        return res

    def get_available_updates(self, cr, uid, ids, modules):
        return self.__for_each_module(cr, uid, ids, modules, lambda m: m.version)

    def retrieve_updates(self, cr, uid, ids, modules):
        return self.__for_each_module(cr, uid, ids, modules, lambda m: addons.get_module_as_zip_from_module_directory(m.path, b64enc=True))

    def submit(self, cr, uid, id, tb, explanations, remarks=None, origin=None):
        contract = self.browse(cr, uid, id)
        
        origin_to_channelname = {
            'client': 'Client Bug Reporting Form',
            'openerp.com': 'OpenERP.com Web Form',
        }
        channelname = origin_to_channelname.get(origin)

        if channelname:
            channelobj = self.pool.get('res.partner.canal')
            channelid = channelobj.search(cr, uid, [('name', '=', channelname)])
            channelid = channelid and channelid[0] or None
            if not channelid:
                channelid = channelobj.create(cr, uid, {'name': channelname})
        else:
            channelid = False   # no Channel for the CRM Case
        

        crmcase = self.pool.get('crm.case')
        desc = "%s\n\n-----\n%s" % (explanations, tb)
        if remarks:
            desc = "%s\n\n----\n%s" % (desc, remarks)
        
        caseid = crmcase.create(cr, uid, {
            'name': 'Maintenance report from %s' % (contract.name),
            'section_id': contract.type_id.crm_case_section_id.id,
            'categ_id': contract.type_id.crm_case_categ_id.id,
            'partner_id': contract.partner_id.id,
            'description': desc,
            'canal_id': channelid,
        })
        crmcase.case_log(cr, uid, [caseid])
        return caseid

maintenance_maintenance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

