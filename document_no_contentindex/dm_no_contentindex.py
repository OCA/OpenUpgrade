# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution····
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

from osv import fields
from osv import osv
import netsvc

class document_file(osv.osv):
    _inherit = 'ir.attachment'
    _columns = {
        'no_index_content' : fields.boolean('No Index Content'),
    }
    _defaults = {
        'no_index_content' : lambda *a: True 
    }
    def write(self, cr, uid, ids, vals, context=None):
        res=self.search(cr,uid,[('id','in',ids)])
        if not len(res):
            return False
        if not self._check_duplication(cr,uid,vals,ids,'write'):
            raise except_orm(_('ValidateError'), _('File name must be unique!'))
        result = super(document_file,self).write(cr,uid,ids,vals,context=context)
        cr.commit()
        if 'no_index_content' in vals and vals['no_index_content']:
            self.write(cr, uid, ids, {'index_content': False})
        else:
            try:
                for f in self.browse(cr, uid, ids, context=context):
                    #if 'datas' not in vals:
                    #    vals['datas']=f.datas
                    res = content_index(base64.decodestring(vals['datas']), f.datas_fname, f.file_type or None)
                    super(document_file,self).write(cr, uid, ids, {
                        'index_content': res
                    })
                cr.commit()
            except:
                pass
        return result

    def create(self, cr, uid, vals, context={}):
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
        if 'no_index_content' in vals and vals['no_index_content']:
            self.write(cr, uid, [result], {'index_content': False})
        else:
            try:
                res = content_index(base64.decodestring(datas), vals['datas_fname'], vals.get('content_type', None))
                super(document_file,self).write(cr, uid, [result], {
                    'index_content': res,
                })
                cr.commit()
            except:
                pass
        return result

document_file()