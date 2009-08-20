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
import datetime
import warnings
import sys
import netsvc
import pooler
import base64
import string
import re
import os
import tools
from lxml import etree

from mx import DateTime
from osv import fields
from osv import osv
from random import Random

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import urllib2, urlparse


from dm_report_design import merge_message

_regex = re.compile('\[\[setHtmlImage\((.+?)\)\]\]')
_regexp1 = re.compile('(\[\[.+?\]\])')

class dm_dynamic_text(osv.osv): # {{{
    _name = 'dm.dynamic_text'
    _rec_name = 'content'
    _columns = {
        'language_id' : fields.many2one('res.lang', 'Language', ondelete='cascade'),
        'gender_id' : fields.many2one('partner.gender', 'Gender'),
        'content' : fields.text('Content'),
        'previous_step_id' : fields.many2one('dm.offer.step', 'Previous Step', ondelete='cascade'),
        'ref_text_id' : fields.many2one('dm.dynamic_text', 'Reference Text'),
        }
dm_dynamic_text() # }}}

class dm_dtp_plugin(osv.osv): # {{{
    _name = "dm.dtp.plugin"

    def copy(self, cr, uid, id, default=None, context={}):
        if not default:
            default = {}
        data = self.browse(cr, uid, id, context)
        default['code'] = (data['code'] or '') + '(copy)'
        return super(dm_dtp_plugin, self).copy(cr, uid, id, default, context=context)

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
        cr.execute('select id, file_fname from dm_dtp_plugin where id in ('+', '.join(map(str, ids))+')')
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
        print "Plugin result :", plugin_res
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

dm_dtp_plugin() # }}}

class dm_plugin_argument(osv.osv): # {{{
    _name = "dm.plugin.argument"
    _description = "Argument List"
    _columns = {
        'name' : fields.char('Argument Name', size=64,required=True),
        'value' : fields.text('Argument Value', size=64),
        'plugin_id' : fields.many2one('dm.dtp.plugin','Plugin'),
        'note' : fields.text('Description',readonly=True),
        'stored_plugin' : fields.boolean('Value from plugin'),
        'custome_plugin_id' : fields.many2one('dm.dtp.plugin','Plugin For Value'),
        }
dm_plugin_argument() # }}}

class dm_document_template(osv.osv): # {{{
    _name = "dm.document.template"
    _columns = {
        'name' : fields.char('Template Name', size=128),
        'plugin_ids' : fields.many2many('dm.dtp.plugin','dm_template_plugin_rel','dm_dtp_plugin_id','dm_document_template_id', 'Plugin'),
        'note' : fields.text('Description')
        }
    
dm_document_template() # }}}

class dm_plugins_value(osv.osv): # {{{
    _name = "dm.plugins.value"
    _columns = {
#        'address_id' : fields.many2one('res.partner.address', 'Customer Address', ondelete="cascade"),
        'workitem_id' : fields.many2one('dm.workitem', 'Workitem', ondelete="cascade"),
        'plugin_id' : fields.many2one('dm.dtp.plugin', 'Plugin'),
        'value' : fields.text('Value'),
#        'date' : fields.date('Date'),
    }
    
dm_plugins_value() # }}}

def set_image_email(node,msg):
    if not node.getchildren():
        if  node.tag=='img' and node.get('src') :
            content = ''
            if node.get('src').find('data:image/gif;base64,')>=0:
                content = base64.decodestring(node.get('src').replace('data:image/gif;base64,',''))
            elif node.get('src').find('http')>=0:
                content=urllib2.urlopen(node.get('src')).read()
            msgImage = MIMEImage(content)
            image_name = ''.join( Random().sample(string.letters+string.digits, 12) )
            msgImage.add_header('Content-ID','<%s>'%image_name)
            msg.attach(msgImage)
            node.set('src',"cid:%s"%image_name)
    else :
        for n in node.getchildren():
            set_image_email(n,msg)

def create_email_queue(cr,uid,obj,context):
    pool = pooler.get_pool(cr.dbname)
    ir_att_obj = pool.get('ir.attachment')
    email_queue_obj = pool.get('email.smtpclient.queue')
    ir_att_ids = ir_att_obj.search(cr,uid,[('res_model','=','dm.campaign.document'),('res_id','=',obj.id),('file_type','=','html')])
    context['document_id'] = obj.document_id.id
    context['address_id'] = obj.address_id.id


    for attach in ir_att_obj.browse(cr,uid,ir_att_ids):
        message = base64.decodestring(attach.datas)
        root = etree.HTML(message)
        body = root.find('body')
        msgRoot = MIMEMultipart('related')

#        plugin_list = [] 
#        No need as it is set in the function
#        if obj.document_id.subject and _regexp1.findall(obj.document_id.subject) :
#            raw_plugin_list = _regexp1.findall(obj.document_id.subject)
#            for p in raw_plugin_list :
#                plugin_list.append(p[2:-2])
#        context['plugin_list'] = plugin_list'''
        subject =  merge_message(cr, uid, obj.document_id.subject, context)
        msgRoot['Subject'] = subject
        msgRoot['From'] = str(obj.mail_service_id.smtp_server_id.email)
        msgRoot['To'] = str(obj.address_id.email)
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
    
        msg = MIMEMultipart('alternative')
        msgRoot.attach(msg)

        set_image_email(body,msgRoot)
        msgText = MIMEText(etree.tostring(body), 'html')
        msg.attach(msgText)
        if message :
            vals = {
                'to':str(obj.address_id.email),
                'server_id':obj.mail_service_id.smtp_server_id.id,
                'cc':False,
                'bcc':False,
                'name':subject,
                'body' : msgRoot.as_string(),
                'serialized_message': msgRoot.as_string(),
                'date_create':time.strftime('%Y-%m-%d %H:%M:%S')
                }
            email_queue_obj.create(cr,uid,vals)
    return True

class dm_offer_document_category(osv.osv): # {{{
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

dm_offer_document_category() # }}}


class dm_offer_document(osv.osv): # {{{
    _name = "dm.offer.document"
    _rec_name = 'name'

    def _check_unique_category(self, cr, uid, ids, step_id, category_id):
        if not (step_id and category_id):
            return {}
        browse_step_id = self.pool.get('dm.offer.step').browse(cr,uid,step_id)
        categ_name = self.pool.get('dm.offer.document.category').browse(cr,uid,category_id).name
        if categ_name == 'After-Sale Document Template' and browse_step_id.type_id.name in ['After-Sale Event','After-Sale Action']:
            if self.search(cr,uid,[('step_id','=',step_id),('category_id','=',category_id)]):
                raise osv.except_osv(_('Error'),
                                 _("You cannot create more than 1 document with the After-Sale step and category - '%s'") % (categ_name,))
        return {'value':{'category_id':category_id}}

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
        'category_id' : fields.many2one('dm.offer.document.category', 'Category', required=True),
        'step_id': fields.many2one('dm.offer.step', 'Offer Step'),
        'has_attachment' : fields.function(_has_attchment_fnc, method=True, type='char', string='Has Attachment'),
        'document_template_id' : fields.many2one('dm.document.template', 'Document Template',),
        'document_template_plugin_ids' : fields.many2many('dm.dtp.plugin','dm_doc_template_plugin_rel',
              'document_id','document_template_plugin_id','Dynamic Plugins',),
        'state' : fields.selection([('draft','Draft'),('validate','Validated')], 'Status', readonly=True),
        'note' : fields.text('Description'),
#        'gender_id' : fields.many2one('res.partner.title', 'Gender' ,domain=[('domain','=','contact')]),
        'gender_id' : fields.many2one('partner.gender', 'Gender', ondelete="cascade"),
        'subject' : fields.char('Object',size=128),
        'editor' : fields.selection([('internal','Internal'),('oord','DM Open Office Report Design')],'Editor'),
        'content' : fields.text('Content'),
        'media_id':fields.related('step_id','media_id','name',type='char', relation='dm.media', string='Media'),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    def state_validate_set(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'validate'})
        return True
  
dm_offer_document() # }}}

class dm_campaign_document_type(osv.osv): # {{{
    _name = 'dm.campaign.document.type'
    _columns = {
            'name' : fields.char('Name', size=64, required=True),
            'code' : fields.char('Code', size=64, required=True),
            }
dm_campaign_document_type() # }}}

class dm_campaign_document(osv.osv): # {{{
    _name = 'dm.campaign.document'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'type_id' : fields.many2one('dm.campaign.document.type','Format',required=True),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment'),
        'delivery_time': fields.datetime('Delivery Time', readonly=True),
        'mail_service_id' : fields.many2one('dm.mail_service','Mail Service',ondelete='cascade',),
        'state' : fields.selection([('pending','Pending'),('done','Done'),('error','Error'),],'State'),
        'error_msg' : fields.text('System Message'),
        'document_id' : fields.many2one('dm.offer.document','Document',ondelete="cascade"),
        'address_id' : fields.many2one('res.partner.address', 'Customer Address', select="1", ondelete="cascade"),
        'origin' : fields.char('Origin', size=64),
        'wi_id' : fields.many2one('dm.workitem','Workitem'),
        }
    _defaults = {
        'state': lambda *a : 'pending',
       }
dm_campaign_document() # }}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
