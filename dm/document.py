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
import sys
from osv import fields
from osv import osv
import pooler
import os
import base64
import tools


class dm_dynamic_text(osv.osv):
    _name = 'dm.dynamic_text'
    _rec_name = 'content'
    _columns = {
        'language_id' : fields.many2one('res.lang','Language',ondelete='cascade'),
        'gender_id' : fields.many2one('res.partner.title', 'Gender', domain="[('domain','=','contact')]"),
        'content' : fields.text('Content'),
        'previous_step_id' : fields.many2one('dm.offer.step','Previous Step',ondelete='cascade'),
        'ref_text_id' : fields.many2one('dm.dynamic_text', 'Reference Text'),
        }
dm_dynamic_text()


class dm_dtp_plugin(osv.osv):
    _name = "dm.dtp.plugin"

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context and 'dm_template_id' in context:
            if not context['dm_template_id']:
                return []
            res = self.pool.get('dm.document.template').browse(cr, uid, context['dm_template_id'])
            plugin_ids = map(lambda x : x.id, res.plugin_ids)
            return plugin_ids
        return super(dm_dtp_plugin, self).search(cr, uid, args, offset, limit, order, context, count)

    def _data_get(self, cr, uid, ids, name, arg, context):
        result = {}
        cr.execute('select id, file_fname from dm_dtp_plugin where id in ('+','.join(map(str, ids))+')')
        for id, r in cr.fetchall():
            try:
                path = os.path.join(os.getcwd(), "addons/dm/dm_dtp_plugins", cr.dbname)
                value = file(os.path.join(path, r), 'rb').read()
                result[id] = base64.encodestring(value)
            except:
                result[id] = ''
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        if not value:
            return True
        sql = "select file_fname from dm_dtp_plugin where id = %d" %id
        cr.execute(sql) 
        res = cr.fetchone()

        path = os.path.join(os.getcwd(), "addons/dm/dm_dtp_plugins", cr.dbname)
        if not os.path.isdir(path):
            os.makedirs(path)
        filename = res[0]
        fname = os.path.join(path, filename)
        fp = file(fname, 'wb')
        v = base64.decodestring(value)
        fp.write(v)
        fp.close()
        plugin_res = self.browse(cr,uid,id)
        print plugin_res
        sys.path.append(path)
        X =  __import__(filename.split('.')[0])
        args = []
        if '__args__' in dir(X):
            args = X.__args__
        plugin_argument = self.pool.get('dm.plugin.argument')
        for arg in args:
            arg_id = plugin_argument.search(cr,uid,[('name','=',arg[0]),('plugin_id','=',id)])
            if not arg_id:
                desc = 'Value of the field must be of type %s or plugin may be crashed' %arg[1]
                vals = {'name':arg[0], 'note':desc, 'plugin_id':id, 'value':' '}
                new_id = plugin_argument.create(cr, uid, vals)
        if '__description__' in dir(X) and not plugin_res.note :
            self.write(cr, uid, id, {'note':str(X.__description__)})
        return True

    def create(self,cr,uid,vals,context={}):
        id = super(dm_dtp_plugin,self).create(cr,uid,vals,context)
        if vals['type'] == 'url' :
            plugin_argument = self.pool.get('dm.plugin.argument')
            plugin_argument.create(cr, uid,{'name':'text_display', 'note':'Value of the field must be of type string or plugin may be crashed', 'plugin_id':id, 'value':' '} )
            plugin_argument.create(cr, uid,{'name':'url', 'note':'Value of the field must be of type string or plugin may be crashed', 'plugin_id':id, 'value':' '} )
        return id

    _columns = {
        'name' : fields.char('DTP Plugin Name', size=64),
        'store_value' : fields.boolean('Store Value'),
        'code' : fields.char('Code', size=64 , required=True),
        'file_id': fields.function(_data_get, method=True, fnct_inv=_data_set, string='File Content', type="binary"),
        'file_fname': fields.char('Filename',size=64),
        'argument_ids' : fields.one2many('dm.plugin.argument', 'plugin_id', 'Argument List'),
        'note' : fields.text('Description'),
        'type' : fields.selection([('fields','Customer'),('dynamic','Dynamic'),('url','URL'),('dynamic_text','Dynamic Text'),('image','Trademark Image')], 'Type', required=True),
        'model_id' : fields.many2one('ir.model','Object'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field'),
        'encode' : fields.boolean('Encode Url Parameters'),
        'python_code' :fields.text('Python Code', help="Python code to be executed"),
#        'key' : fields.char('DES Key',size=64),
        'ref_text_id' : fields.many2one('dm.dynamic_text','Reference Text'),
        'preview_value' :fields.char('Preview Text',size=64),
     }
    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The code must be unique!'),
    ]

dm_dtp_plugin()

class dm_plugin_argument(osv.osv):
    _name = "dm.plugin.argument"
    _description = "Argument List"
    _columns = {
        'name' : fields.char('Argument Name', size=64,required=True),
        'value' : fields.text('Argument Value', size=64),
        'plugin_id' : fields.many2one('dm.dtp.plugin','Plugin'),
        'note' : fields.text('Description',readonly=True),
        'stored_plugin' : fields.boolean('Value from plugin'),
        'custome_plugin_id' : fields.many2one('dm.dtp.plugin','Plugin For Value' ,domain=[('type','=','fields')]),
        }
dm_plugin_argument()

class dm_document_template(osv.osv):
    _name = "dm.document.template"
    _columns = {
        'name' : fields.char('Template Name', size=128),
        'plugin_ids' : fields.many2many('dm.dtp.plugin','dm_template_plugin_rel','dm_dtp_plugin_id','dm_document_template_id', 'Plugin'),
        'note' : fields.text('Description')
        }
    
dm_document_template()

class dm_plugins_value(osv.osv):
    _name = "dm.plugins.value"
    _columns = {
        'address_id' : fields.many2one('res.partner.address', 'Customer Address', ondelete="cascade"),
        'plugin_id' : fields.many2one('dm.dtp.plugin', 'Plugin'),
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
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context)
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

class dm_offer_document(osv.osv):
    _name = "dm.offer.document"
    _rec_name = 'name'

    def default_get(self, cr, uid, fields, context=None):
        value = super(dm_offer_document, self).default_get(cr, uid, fields, context)
        if 'step_id' in context and context['step_id']:
            offer = self.pool.get('dm.offer')
            offer_id = offer.search(cr, uid, [('step_ids', 'in', [context['step_id']])])
            browse_id = offer.browse(cr, uid, offer_id)[0]
            value['lang_id'] = browse_id.lang_orig_id.id
            value['copywriter_id'] = browse_id.copywriter_id.id
        return value

    def _has_attchment_fnc(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for id in ids :
            attachment_id = self.pool.get('ir.attachment').search(cr, uid, [('res_model', '=', 'dm.offer.document'), ('res_id', '=', id)])
            if attachment_id :
                res[id] = True
            else :  
                res[id] = False
        return res

    def onchange_plugin(self, cr, uid, ids, document_template_id):
        res = {'value':{}}
        if document_template_id:
            template = self.pool.get('dm.document.template').read(cr, uid, [document_template_id])[0]
            res['value'] = {'document_template_plugin_ids':template['plugin_ids']}
        return res

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'lang_id' : fields.many2one('res.lang', 'Language', required=True),
        'copywriter_id' : fields.many2one('res.partner', 'Copywriter', domain=[('category_id','ilike','Copywriter')], context={'category':'Copywriter'}),
        'category_id' : fields.many2one('dm.offer.document.category', 'Category'),
        'step_id': fields.many2one('dm.offer.step', 'Offer Step'),
        'has_attachment' : fields.function(_has_attchment_fnc, method=True, type='char', string='Has Attachment'),
        'document_template_id' : fields.many2one('dm.document.template', 'Document Template',),
        'document_template_plugin_ids' : fields.many2many('dm.dtp.plugin','dm_doc_template_plugin_rel',
              'document_id','document_template_plugin_id','Dynamic Plugins',),
        'state' : fields.selection([('draft','Draft'),('validate','Validated')], 'Status', readonly=True),
        'note' : fields.text('Description'),
        'gender_id' : fields.many2one('res.partner.title', 'Gender' ,domain=[('domain','=','contact')]),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    def state_validate_set(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'validate'})
        return True
  
dm_offer_document()

class dm_campaign_document_type(osv.osv):
    _name = 'dm.campaign.document.type'
    _columns = {
            'name' : fields.char('Name', size=64, required=True),
            'code' : fields.char('Code', size=64, required=True),
            }
dm_campaign_document_type()

class dm_campaign_document(osv.osv):
    _name = 'dm.campaign.document'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'type_id' : fields.many2one('dm.campaign.document.type','Format',required=True),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment',required=True),
        'delivery_time': fields.datetime('Delivery Time', readonly=True),
        'mail_service_id' : fields.many2one('dm.mail_service','Mail Service',ondelete='cascade',),
        'state' : fields.selection([('pending','Pending'),('done','Done'),('error','Error'),],'State'),
        'error_msg' : fields.text('System Message'),
        'document_id' : fields.many2one('dm.offer.document','Document',ondelete="cascade"),
        'address_id' : fields.many2one('res.partner.address', 'Customer Address', select="1", ondelete="cascade"),
        }
    _defaults = {
        'state': lambda *a : 'pending',
        }
        
dm_campaign_document()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
