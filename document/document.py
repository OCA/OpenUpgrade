# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import base64

from osv import osv, fields
from osv.orm import except_orm
import urlparse

import os

import pooler
from content_index import cntIndex
import netsvc
import StringIO

import random
import string
from psycopg2 import Binary
from tools import config
import tools
from tools.translate import _

def random_name():
    random.seed()
    d = [random.choice(string.ascii_letters) for x in xrange(10) ]
    name = "".join(d)
    return name


# Unsupported WebDAV Commands:
#     label
#     search
#     checkin
#     checkout
#     propget
#     propset

#
# An object that represent an uri
#   path: the uri of the object
#   content: the Content it belongs to (_print.pdf)
#   type: content or collection
#       content: objct = res.partner
#       collection: object = directory, object2 = res.partner
#       file: objct = ir.attachement
#   root: if we are at the first directory of a ressource
#
INVALID_CHARS={'*':str(hash('*')), '|':str(hash('|')) , "\\":str(hash("\\")), '/':'__', ':':str(hash(':')), '"':str(hash('"')), '<':str(hash('<')) , '>':str(hash('>')) , '?':str(hash('?'))}


class node_class(object):
    def __init__(self, cr, uid, path, object, object2=False, context={}, content=False, type='collection', root=False):
        self.cr = cr
        self.uid = uid
        self.path = path
        self.object = object
        self.object2 = object2
        self.context = context
        self.content = content
        self.type=type
        self.root=root

    def _file_get(self, nodename=False):
        if not self.object:
            return []
        pool = pooler.get_pool(self.cr.dbname)
        fobj = pool.get('ir.attachment')
        res2 = []
        where = []
        if self.object2:
            where.append( ('res_model','=',self.object2._name) )
            where.append( ('res_id','=',self.object2.id) )
        else:
            where.append( ('parent_id','=',self.object.id) )
            where.append( ('res_id','=',False) )
        if nodename:
            where.append( (fobj._rec_name,'=',nodename) )
        for content in self.object.content_ids:
	    res3 = content._table._file_get(self,nodename,content)
	    if res3:
		res2.extend(res3)

        ids = fobj.search(self.cr, self.uid, where+[ ('parent_id','=',self.object and self.object.id or False) ])
        if self.object and self.root and (self.object.type=='ressource'):
            ids += fobj.search(self.cr, self.uid, where+[ ('parent_id','=',False) ])
        res = fobj.browse(self.cr, self.uid, ids, context=self.context)
        return map(lambda x: node_class(self.cr, self.uid, self.path+'/'+eval('x.'+fobj._rec_name), x, False, context=self.context, type='file', root=False), res) + res2
    
    def get_translation(self,value,lang):
        result = value
        pool = pooler.get_pool(self.cr.dbname)        
        translation_ids = pool.get('ir.translation').search(self.cr, self.uid, [('value','=',value),('lang','=',lang),('type','=','model')])
        if len(translation_ids):
            tran_id = translation_ids[0]
            translation = pool.get('ir.translation').read(self.cr, self.uid, tran_id, ['res_id','name'])
            res_model,field_name = tuple(translation['name'].split(','))  
            res_id = translation['res_id']        
            res = pool.get(res_model).read(self.cr, self.uid, res_id, [field_name])
            if res:
                result = res[field_name]
        return result 
    
    def directory_list_for_child(self,nodename,parent=False):
        pool = pooler.get_pool(self.cr.dbname)
        where = []
        if nodename:
            nodename = self.get_translation(nodename, self.context['lang'])
            where.append(('name','=',nodename))
        if (self.object and self.object.type=='directory') or not self.object2:
            where.append(('parent_id','=',self.object and self.object.id or False))
        else:
            where.append(('parent_id','=',False))
        if self.object:
            where.append(('ressource_parent_type_id','=',self.object.ressource_type_id.id))
        else:
            where.append(('ressource_parent_type_id','=',False))

        ids = pool.get('document.directory').search(self.cr, self.uid, where+[('ressource_id','=',0)])
        if self.object2:
            ids += pool.get('document.directory').search(self.cr, self.uid, where+[('ressource_id','=',self.object2.id)])        
        res = pool.get('document.directory').browse(self.cr, self.uid, ids, self.context)
        return res

    def _child_get(self, nodename=False):
        if self.type not in ('collection','database'):
            return []
        res = self.directory_list_for_child(nodename)
        result= map(lambda x: node_class(self.cr, self.uid, self.path+'/'+x.name, x, x.type=='directory' and self.object2 or False, context=self.context, root=self.root), res)
        if self.type=='database':
            pool = pooler.get_pool(self.cr.dbname)
            fobj = pool.get('ir.attachment')
            vargs = [('parent_id','=',False),('res_id','=',False)]
            if nodename:
                vargs.append((fobj._rec_name,'=',nodename))
            file_ids=fobj.search(self.cr,self.uid,vargs)

            res = fobj.browse(self.cr, self.uid, file_ids, context=self.context)
            result +=map(lambda x: node_class(self.cr, self.uid, self.path+'/'+eval('x.'+fobj._rec_name), x, False, context=self.context, type='file', root=self.root), res)
        if self.type=='collection' and self.object.type=="ressource":
            where = self.object.domain and eval(self.object.domain, {'active_id':self.root, 'uid':self.uid}) or []
            pool = pooler.get_pool(self.cr.dbname)
            obj = pool.get(self.object.ressource_type_id.model)
            _dirname_field = obj._rec_name
            if len(obj.fields_get(self.cr, self.uid, ['dirname'])):
                _dirname_field = 'dirname'

            name_for = obj._name.split('.')[-1]
            if nodename  and nodename.find(name_for) == 0  :
                id = int(nodename.replace(name_for,''))
                where.append(('id','=',id))
            elif nodename:
                if nodename.find('__') :
                    nodename=nodename.replace('__','/')
                for invalid in INVALID_CHARS:
                    if nodename.find(INVALID_CHARS[invalid]) :
                        nodename=nodename.replace(INVALID_CHARS[invalid],invalid)
                nodename = self.get_translation(nodename, self.context['lang'])
                where.append((_dirname_field,'=',nodename))

            if self.object.ressource_tree:
                if obj._parent_name in obj.fields_get(self.cr,self.uid):
                    where.append((obj._parent_name,'=',self.object2 and self.object2.id or False))
                    ids = obj.search(self.cr, self.uid, where)
                    res = obj.browse(self.cr, self.uid, ids,self.context)
                    result+= map(lambda x: node_class(self.cr, self.uid, self.path+'/'+x.name.replace('/','__'), self.object, x, context=self.context, root=x.id), res)
                    return result
                else :
                    if self.object2:
                        return result
            else:
                if self.object2:
                    return result

            
            ids = obj.search(self.cr, self.uid, where)
            res = obj.browse(self.cr, self.uid, ids,self.context)
            for r in res:
                if len(obj.fields_get(self.cr, self.uid, [_dirname_field])):
                    r.name = eval('r.'+_dirname_field)
                else:
                    r.name = False
                if not r.name:
                    r.name = name_for + '%d'%r.id
                for invalid in INVALID_CHARS:
                    if r.name.find(invalid) :
                        r.name = r.name.replace(invalid,INVALID_CHARS[invalid])
            result2 = map(lambda x: node_class(self.cr, self.uid, self.path+'/'+x.name.replace('/','__'), self.object, x, context=self.context, root=x.id), res)
            if result2:
                if self.object.ressource_tree:
                    result += result2
                else:
                    result = result2
        return result

    def children(self):
        return self._child_get() + self._file_get()

    def child(self, name):
        res = self._child_get(name)
        if res:
            return res[0]
        res = self._file_get(name)
        if res:
            return res[0]
        return None

    def path_get(self):
        path = self.path
        if self.path[0]=='/':
            path = self.path[1:]
        return path

def create_directory(path):
    dir_name = random_name()
    path = os.path.join(path,dir_name)
    os.makedirs(path)
    return dir_name

class document_file(osv.osv):
    _inherit = 'ir.attachment'
    _rec_name = 'datas_fname'
    def _get_filestore(self, cr):
        return os.path.join(tools.config['root_path'], 'filestore', cr.dbname)

    def _data_get(self, cr, uid, ids, name, arg, context):
        result = {}
        cr.execute('select id,store_fname,link from ir_attachment where id in ('+','.join(map(str,ids))+')')
        for id,r,l in cr.fetchall():
            try:
                value = file(os.path.join(self._get_filestore(cr), r), 'rb').read()
                result[id] = base64.encodestring(value)
            except:
                result[id]=''

            if context.get('bin_size', False):
                result[id] = tools.human_size(len(result[id]))

        return result

    #
    # This code can be improved
    #
    def _data_set(self, cr, obj, id, name, value, uid=None, context={}):
        if not value:
            return True
        #if (not context) or context.get('store_method','fs')=='fs':
        try:
            path = self._get_filestore(cr)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except:
                    raise except_orm(_('Permission Denied !'), _('You do not permissions to write on the server side.'))

            flag = None
            # This can be improved
            for dirs in os.listdir(path):
                if os.path.isdir(os.path.join(path,dirs)) and len(os.listdir(os.path.join(path,dirs)))<4000:
                    flag = dirs
                    break
            flag = flag or create_directory(path)
            filename = random_name()
            fname = os.path.join(path, flag, filename)
            fp = file(fname,'wb')
            v = base64.decodestring(value)
            fp.write(v)
            filesize = os.stat(fname).st_size
            cr.execute('update ir_attachment set store_fname=%s,store_method=%s,file_size=%s where id=%s', (os.path.join(flag,filename),'fs',len(v),id))
            return True
        except Exception,e :
            raise except_orm(_('Error!'), str(e))

    _columns = {
        'user_id': fields.many2one('res.users', 'Owner', select=1),
        'group_ids': fields.many2many('res.groups', 'document_directory_group_rel', 'item_id', 'group_id', 'Groups'),
        'parent_id': fields.many2one('document.directory', 'Directory', select=1),
        'file_size': fields.integer('File Size', required=True),
        'file_type': fields.char('Content Type', size=32),
	# If ir.attachment contained any data before document is installed, preserve
	# the data, don't drop the column!
	'db_datas': fields.binary('Data',oldname='datas'),
        'index_content': fields.text('Indexed Content'),
        'write_date': fields.datetime('Date Modified', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'create_uid':  fields.many2one('res.users', 'Creator', readonly=True),
        'store_method': fields.selection([('db','Database'),('fs','Filesystem'),('link','Link')], "Storing Method"),
        'datas': fields.function(_data_get,method=True,fnct_inv=_data_set,string='File Content',type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=200),
        'res_model': fields.char('Attached Model', size=64), #res_model
        'res_id': fields.integer('Attached ID'), #res_id
        'partner_id':fields.many2one('res.partner', 'Partner', select=1),
        'title': fields.char('Resource Title',size=64),
    }

    _defaults = {
        'user_id': lambda self,cr,uid,ctx:uid,
        'file_size': lambda self,cr,uid,ctx:0,
        'store_method': lambda *args: 'db'
    }
    _sql_constraints = [
        ('filename_uniq', 'unique (name,parent_id,res_id,res_model)', 'The file name must be unique !')
    ]
    def _check_duplication(self, cr, uid,vals,ids=[],op='create'):
        name=vals.get('name',False)
        parent_id=vals.get('parent_id',False)
        res_model=vals.get('res_model',False)
        res_id=vals.get('res_id',0)
        if op=='write':
            for file in self.browse(cr,uid,ids):
                if not name:
                    name=file.name
                if not parent_id:
                    parent_id=file.parent_id and file.parent_id.id or False
                if not res_model:
                    res_model=file.res_model and file.res_model or False
                if not res_id:
                    res_id=file.res_id and file.res_id or 0
                res=self.search(cr,uid,[('id','<>',file.id),('name','=',name),('parent_id','=',parent_id),('res_model','=',res_model),('res_id','=',res_id)])
                if len(res):
                    return False
        if op=='create':
            res=self.search(cr,uid,[('name','=',name),('parent_id','=',parent_id),('res_id','=',res_id),('res_model','=',res_model)])
            if len(res):
                return False
        return True
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default ={}
        name = self.read(cr, uid, [id])[0]['name']
        default.update({'name': name+ " (copy)"})
        return super(document_file,self).copy(cr,uid,id,default,context)
    def write(self, cr, uid, ids, vals, context=None):
        res=self.search(cr,uid,[('id','in',ids)])
        if not len(res):
            return False
        if not self._check_duplication(cr,uid,vals,ids,'write'):
            raise except_orm(_('ValidateError'), _('File name must be unique!'))
        result = super(document_file,self).write(cr,uid,ids,vals,context=context)
        cr.commit()
        try:
            for f in self.browse(cr, uid, ids, context=context):
                #if 'datas' not in vals:
                #    vals['datas']=f.datas
		mime,res = cntIndex.doIndex(base64.decodestring(vals['datas']), f.datas_fname, 
			f.file_type or None,f.store_fname)
		wval = {'index_content': res,}
		if (not f.file_type ) and mime:
			wval['file_type'] = mime
		super(document_file,self).write(cr, uid, [f.id], wval )
            cr.commit()
        except Exception,e:
	    logger = netsvc.Logger()
	    logger.notifyChannel('document', netsvc.LOG_DEBUG, 'Cannot index file: %s' % str(e))
            pass
        return result

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        vals['title']=vals['name']
        vals['parent_id'] = context.get('parent_id',False) or vals.get('parent_id',False)
        if not vals.get('res_id', False) and context.get('default_res_id',False):
            vals['res_id']=context.get('default_res_id',False)
        if not vals.get('res_model', False) and context.get('default_res_model',False):
            vals['res_model']=context.get('default_res_model',False)
        if vals.get('res_id', False) and vals.get('res_model',False):
            obj_model=self.pool.get(vals['res_model'])
            result = obj_model.read(cr, uid, [vals['res_id']], context=context)
            if len(result):
                obj=result[0]
                if obj.get('name',False):
                    vals['title'] = (obj.get('name',''))[:60]
                if obj_model._name=='res.partner':
                    vals['partner_id']=obj['id']
                elif obj.get('address_id',False):
                    if isinstance(obj['address_id'],tuple) or isinstance(obj['address_id'],list):
                        address_id=obj['address_id'][0]
                    else:
                        address_id=obj['address_id']
                    address=self.pool.get('res.partner.address').read(cr,uid,[address_id],context=context)
                    if len(address):
                        vals['partner_id']=address[0]['partner_id'][0] or False
                elif obj.get('partner_id',False):
                    if isinstance(obj['partner_id'],tuple) or isinstance(obj['partner_id'],list):
                        vals['partner_id']=obj['partner_id'][0]
                    else:
                        vals['partner_id']=obj['partner_id']

        datas=None
        if vals.get('link',False) :
            import urllib
            datas=base64.encodestring(urllib.urlopen(vals['link']).read())
        else:
            datas=vals.get('datas',False)
        vals['file_size']= len(datas)
        if not self._check_duplication(cr,uid,vals):
            raise except_orm(_('ValidateError'), _('File name must be unique!'))
        result = super(document_file,self).create(cr, uid, vals, context)
        cr.commit()
        try:
            mime,res = cntIndex.doIndex(base64.decodestring(datas), vals['datas_fname'], 
		vals.get('file_type', None),vals.get('store_fname',None))
	    wval = {'index_content': res,}
	    if (not vals.get('file_type',False)) and mime:
		wval['file_type'] = mime
            super(document_file,self).write(cr, uid, [result], wval )
            cr.commit()
        except Exception,e:
	    logger = netsvc.Logger()
	    logger.notifyChannel('document', netsvc.LOG_DEBUG, 'Cannot index file: %s' % str(e))
            pass
        return result

    def unlink(self,cr, uid, ids, context={}):
        for f in self.browse(cr, uid, ids, context):
            #if f.store_method=='fs':
            try:
                os.unlink(os.path.join(self._get_filestore(cr), f.store_fname))
            except:
                pass
        return super(document_file, self).unlink(cr, uid, ids, context)
document_file()

