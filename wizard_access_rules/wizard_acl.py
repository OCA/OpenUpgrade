#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

from osv import fields,osv
from tools.translate import _

class wizard_acl_list(osv.osv_memory):
    _name = 'wizard.acl.list'
    
    _columns = {
        'name':fields.char('Name', size=64, required=False, readonly=False),
        'acl_ids':fields.one2many('wizard.acl', 'acllist_id', 'Access Control'),
    }
   
    def action_cancel(self, cr, uid, ids, conect=None):
        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'ir.actions.configuration.wizard',
            'type': 'ir.actions.act_window',
            'target':'new',
         }
         
    def get_list(self, cr, uid, ids, conect=None):
        cr.execute("""select id, model, name from ir_model where id not in (select model_id from ir_model_access)""")
        for (id, model, name) in cr.fetchall():
            self.pool.get('wizard.acl').create(cr, uid, {'acllist_id':ids[0], 'name':model, 'group_id':False, 'object_id':id})
        return True
        
    def action_create(self, cr, uid, ids, conect=None):
        acl_pool = self.pool.get('ir.model.access')
        wizacl_pool = self.pool.get('wizard.acl')

        for res in self.browse(cr, uid, ids[0]).acl_ids:
            mid = res.object_id.id
            gid = res.group_id.id
            
            acl_pool.create(cr, uid, {
                'name':res.name,
                'model_id':res.object_id.id,
                'group_id': res.group_id and res.group_id.id or False,
                'perm_read':res.read,
                'perm_write':res.write,
                'perm_create':res.create,
                'perm_unlink':res.unlink,
            })
        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'ir.actions.configuration.wizard',
            'type': 'ir.actions.act_window',
            'target':'new',
         }
wizard_acl_list()

class wizard_acl(osv.osv_memory):
    _name = 'wizard.acl'

    _columns = {
        'acllist_id':fields.many2one('wizard.acl.list', 'Access List', required=False),
        'name':fields.char('Name', size=64, required=False, readonly=False),
        'object_id':fields.many2one('ir.model', 'Model', required=False),
        'group_id':fields.many2one('res.groups', 'Group', required=False),
        'read':fields.boolean('Read', required=False),
        'write':fields.boolean('Write', required=False),
        'create':fields.boolean('Create', required=False),
        'unlink':fields.boolean('Unlink', required=False)
    }
    _defaults = {
        'read': lambda *a: True
    }
wizard_acl()

