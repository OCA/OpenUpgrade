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

from osv import fields
from osv import osv
import pooler
import os
import base64
import tools
import time

class dm_ddf_plugin(osv.osv):
    _name = "dm.ddf.plugin"

    def search(self, cr, uid, args, offset=0, limit=None, order=None,context=None, count=False):
        if 'dm_template_id' in context:
            if not context['dm_template_id']:
                return []
            res = self.pool.get('dm.document.template').browse(cr,uid,context['dm_template_id'])
            plugin_ids = map(lambda x : x.id,res.plugin_ids)
            return plugin_ids
        return super(dm_ddf_plugin,self).search(cr,uid,args,offset,limit,order,context,count)
    
    def _check_plugin(self, cr, uid, ids=False, context={}):
        dm_document = self.pool.get('dm.offer.document')
        dm_plugins_value = self.pool.get('dm.plugins.value')
        ddf_plugin = self.pool.get('dm.ddf.plugin')
        dm_customer_order = self.pool.get('dm.customer.order')
        
        document_ids = dm_document.search(cr,uid,[])
        documents = dm_document.browse(cr,uid,document_ids,['document_template_id','step_id'])
        for d in documents:
            order_id = dm_customer_order.search(cr,uid,[('offer_step_id','=',d.step_id.id)])
            order = dm_customer_order.browse(cr,uid,order_id)
            customer_ids = map(lambda x:x.customer_id.id,order)
            plugins = d.document_template_id.plugin_ids
            for plugin in plugins:
                args={}
                if plugin.field.name:
                    args['field_name']=str(plugin.field.name)
                    args['field_type']=str(plugin.field.ttype)
                    args['field_relation']=str(plugin.field.relation)
                path = os.path.join(os.getcwd(), "addons/dm/dm_ddf_plugins",cr.dbname)
                plugin_name = plugin.file_fname.split('.')[0]
                arguments = plugin.argument_ids
                for a in arguments:
                    args[str(a.name)]=str(a.value)
                import sys
                sys.path.append(path)
                X =  __import__(plugin_name)
                plugin_func = getattr(X,plugin_name)
                plugin_value = plugin_func(cr,uid,customer_ids,**args)

                map(lambda x :dm_plugins_value.create(cr,uid,
                            {'date':time.strftime('%Y-%m-%d'),
                             'customer_id':x[0],
                             'plugin_id':plugin.id,
                             'value' : x[1]}),
                            plugin_value
                            )
        return True
    
    def _data_get(self, cr, uid, ids, name, arg, context):
        result = {}
        cr.execute('select id,file_fname from dm_ddf_plugin where id in ('+','.join(map(str,ids))+')')
        for id ,r in cr.fetchall():            
            try:
                path = os.path.join(os.getcwd(), "addons/dm/dm_ddf_plugins",cr.dbname)
                value = file(os.path.join(path,r), 'rb').read()
                result[id] = base64.encodestring(value)
            except:
                result[id]=''
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        if not value:
            return True
        sql = "select file_fname from dm_ddf_plugin where id = %d"%id
        cr.execute(sql) 
        res = cr.fetchone()

        path = os.path.join(os.getcwd(), "addons/dm/dm_ddf_plugins",cr.dbname)
        if not os.path.isdir(path):
            os.makedirs(path)
        filename = res[0]
        fname = os.path.join(path, filename)
        fp = file(fname,'wb')
        v = base64.decodestring(value)
        fp.write(v)
        fp.close()
        import sys
        sys.path.append(path)
        X =  __import__(filename.split('.')[0])
        args=[]
        if '__args__' in dir(X):
            args = X.__args__
        for arg in args:
            desc = 'Value of the field must be of type %s or plugin may be crashed'%arg[1] 
            vals = {'name':arg[0],'note':desc,'plugin_id':id,'value':' '}
            new_id = self.pool.get('dm.plugin.argument').create(cr,uid,vals)
        print uid
        if '__description__' in dir(X):
            self.write(cr,uid,id,{'note':X.__description__})
        return True
    
    _columns = {
        'name' : fields.char('DDF Plugin Name', size=64),
        'file_id': fields.function(_data_get,method=True,fnct_inv=_data_set,string='File Content',type="binary"),
        'file_fname': fields.char('Filename',size=64),
        'argument_ids' : fields.one2many('dm.plugin.argument', 'plugin_id', 'Argument List'),
        'note' : fields.text('Description'),
        'field' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id','=','Partner')],
               context={'model':'res.partner'}),      
     }
dm_ddf_plugin()

class dm_plugin_argument(osv.osv):
    _name = "dm.plugin.argument"
    _description = "Argument List"
    _columns = {
        'name' : fields.char('Argument Name', size=64,required=True,readonly=True),
        'value' : fields.char('Argument Value', size=64,required=True),
        'plugin_id' : fields.many2one('dm.ddf.plugin','Plugin'),
        'note' : fields.text('Description',readonly=True)
        }
dm_plugin_argument()

class dm_document_template(osv.osv):
    _name = "dm.document.template"
    _columns = {
        'name' : fields.char('Template Name', size=128),
        'plugin_ids' : fields.many2many('dm.ddf.plugin','dm_template_plugin_rel','dm_ddf_plugin_id','dm_document_template_id', 'Plugin'),
        'note' : fields.text('Description')
        }
    
#    def write(self, cr, uid, ids, vals, context=None):
#        res = super(dm_document_template,self).write(cr, uid, ids, vals, context)
#        document_template =self.read(cr,uid,ids)[0]
#        list1 = document_template['dynamic_fields']
#        dm_offer_document = self.pool.get('dm.offer.document')
#        document_ids = dm_offer_document.search(cr,uid,[('document_template_id','=',ids[0])])
#        documents = dm_offer_document.read(cr,uid,document_ids)
#        for doc in documents:
#            list2 = doc['document_template_field_ids'] 
#            diff = list(set(list2).difference(set(list1)))
#            map(lambda x : list2.remove(x) ,diff)
#            dm_offer_document.write(cr,uid,doc['id'],{'document_template_field_ids':[[6, 0,list2]]})
#        return res                 
dm_document_template()

class dm_plugins_value(osv.osv):
    _name = "dm.plugins.value"
    _columns = {
        'customer_id' : fields.many2one('res.partner', 'Customer Name', ondelete="cascade"),
        'plugin_id' : fields.many2one('dm.ddf.plugin', 'Plugin'),
        'value' : fields.char('Value', size=64),
        'date' : fields.date('Date'),
    }
    
dm_plugins_value()

class dm_offer_document_category(osv.osv):
    _name = "dm.offer.document.category"
    _rec_name = "name"
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = self.name_get(cr, uid, ids)
        return dict(res)

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'complete_name' : fields.function(_name_get_fnc, method=True, type='char', string='Category'),
        'parent_id' : fields.many2one('dm.offer.document.category', 'Parent'),
    }

dm_offer_document_category()

#class ir_model_fields(osv.osv):
#    _inherit='ir.model.fields'
#    def search(self, cr, uid, args, offset=0, limit=None, order=None,context=None, count=False):
#        if context:
#            if 'dm_template_id' in context:
#                if not context['dm_template_id']:
#                    return []
#                res = self.pool.get('dm.document.template').browse(cr,uid,context['dm_template_id'])
#                field_id = map(lambda x : x.id,res.dynamic_fields)
#                return field_id
#        return super(ir_model_fields,self).search(cr,uid,args,offset,limit,order,context,count)
#    
#ir_model_fields()

class dm_offer_document(osv.osv):
    _name = "dm.offer.document"
    _rec_name = 'name'
    
    def _has_attchment_fnc(self, cr, uid, ids, name, arg, context={}):
        res={}
        for id in ids :
            attachment_id = self.pool.get('ir.attachment').search(cr,uid,[('res_model','=','dm.offer.document'),('res_id','=',id)])
            if attachment_id :
                res[id]=True
            else :  
                res[id]=False
        return res
    def onchange_plugin(self, cr, uid, ids,document_template_id):
        res={'value':{}}
        if document_template_id:
            template = self.pool.get('dm.document.template').read(cr, uid, [document_template_id])[0]
            res['value']={'document_template_plugin_ids':template['plugin_ids']}
        return res    
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'copywriter_id' : fields.many2one('res.partner', 'Copywriter', domain=[('category_id','ilike','Copywriter')], context={'category':'Copywriter'}),
        'category_ids' : fields.many2many('dm.offer.document.category','dm_offer_document_rel', 'doc_id', 'category_id', 'Categories'),
        'step_id': fields.many2one('dm.offer.step', 'Offer Step'),
        'has_attachment' : fields.function(_has_attchment_fnc, method=True, type='char', string='Has Attachment'),
        'document_template_id' : fields.many2one('dm.document.template', 'Document Template',),
        'document_template_plugin_ids' : fields.many2many('dm.ddf.plugin','dm_doc_template_plugin_rel',
              'document_id','document_template_plugin_id','Dynamic Plugins',),
        'state' : fields.selection([('draft','Draft'),('validate','Validated')], 'Status', readonly=True),
        'note' : fields.text('Description')        
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    def state_validate_set(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'validate'})
        return True
  
dm_offer_document()
