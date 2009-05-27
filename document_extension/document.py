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
import re
from osv import osv, fields
from osv.orm import except_orm
import pooler

class document_directory(osv.osv):
    _inherit='document.directory'
    _columns = {
        'versioning': fields.boolean('Automatic Versioning'),
        'version_regex' : fields.char('Reg. Ex.',size=64,required=True),
        'version_replace': fields.char('Replace',size=64,required=True)
    }
    _defaults={
        'versioning':lambda *a:1,
        'version_regex':lambda *a:'^(.*)(\..*)$',
        'version_replace':lambda *a:"\\1.vcount\\2"
    }
document_directory()
class document_file(osv.osv):
    _inherit = 'ir.attachment'
    _columns = {
        'lock': fields.boolean('Lock',readonly=True),
        'base_res_id':fields.integer('Base Resource')
        }
    _defaults={
        'lock':lambda *a:0,}
    def write(self, cr, uid, ids, vals, context=None):
        for document in self.browse(cr,uid,ids,context=context):
            if document.lock:
                raise osv.except_osv(_('Invalid action !'), _('You Cannot modify  record! Document is Locked'))
            if document.parent_id and document.parent_id.versioning:
                new_datas=vals.get('datas',False)
                if  new_datas and document.datas and document.datas != new_datas:
                     filename=document.datas_fname
                     pattern=document.parent_id.version_regex
                     res=self.search(cr, uid, [('base_res_id' , '=', document.id)])
                     count = len(res) + 1
                     replace=document.parent_id.version_replace.replace('count',str(count))
                     newname=re.sub(pattern,replace, filename)
                     new_vals= {'lock':True,'base_res_id': document.id, 'name':newname,'datas':document.datas,'parent_id':document.parent_id.id,'datas_fname':newname,'partner_id':document.partner_id.id}
                     self.create(cr, uid, new_vals, context=context)
                result = super(document_file,self).write(cr,uid,[document.id],vals,context=context)
        return result
    def unlink(self, cr, uid, ids, context=None):
        for state in self.browse(cr,uid,ids,context=context):
            if state.lock==True:
                raise osv.except_osv(_('Invalid action !'), _('You Cannot delete  record! Document is Locked'))
                try:
                      os.unlink(os.path.join(self._get_filestore(cr), state.store_fname))
                except:
                    pass
            return super(document_file, self).unlink(cr, uid, ids, context)


document_file()
