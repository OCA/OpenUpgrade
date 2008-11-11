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

from osv import osv, fields

# class library_editor_supplier(osv.osv):
#   _name = "library.editor.supplier"
#   _description = "Suppliers associated to an editor"
#   _auto = False
#   _columns = {
#       'name': fields.many2one('res.partner', 'Editor', readonly= True),
#       'supplier_ids' : fields.many2many('res.partner','editor_supplier_rel','editor_id','supplier_id', 'Suppliers',readonly= True),
#   }
#   def init(self, cr):
#       cr.execute("""
#           create or replace view library_editor_supplier as (
#               select editor as id, editor as name from product_product group by editor
#               )
#           """)
# library_editor_supplier()

class library_editor_supplier(osv.osv):
    _name = "library.editor.supplier"
    _description = "many2many view for editor relations"
    _auto = False
    _columns = {
        'name': fields.many2one('res.partner', 'Editor'),
        'supplier_id' : fields.many2one('res.partner', 'Supplier'),
    }

    def init(self, cr):
        cr.execute("""

            create or replace view library_editor_supplier as (
                select
                 case when min(ps.id) is null then - min(pp.id) else min(ps.id) end as id,
                 case when pp.editor is null then 0 else pp.editor end as name,
                 case when ps.name is null then 0 else ps.name end as supplier_id
                from
                 product_supplierinfo ps full outer join product_product pp on (ps.product_id = pp.product_tmpl_id)
                where
                 ((pp.editor is not null) or (ps.name is not null))
                group by pp.editor, ps.name
                 )""")


    def create(self, cr, user, vals, context={}):
        if not (vals['name'] and vals['supplier_id']) : raise osv.except_osv("Error","Please provide ..")
        # search for books of these editor not already linked with this supplier :
        select = 'select product_tmpl_id from product_product where editor = %s and id not in (select product_id from product_supplierinfo where name = %s)'%(vals['name'],vals['supplier_id'])
        cr.execute(select)
        if not cr.rowcount:
            raise osv.except_osv("Error","No book to apply this relation")

        sup_info = self.pool.get('product.supplierinfo')
        last_id = 0
        for book_id in cr.fetchall():
            tmp_id = sup_info.create(cr,user,{'name': vals['supplier_id'], 'product_id': book_id[0]},context)
            last_id = last_id < tmp_id and last_id or tmp_id
        return last_id
    

    def unlink(self, cr, uid, ids, context={}):

        relations = self.browse(cr,uid,ids)
        for rel in relations:
            if not (rel.name and rel.supplier_id) : continue
            # search for the equivalent ids in product_supplierinfo (unpack the group)
            cr.execute("select si.id from product_supplierinfo si join product_product pp on (si.product_id = pp.product_tmpl_id ) where pp.editor = %s and si.name = %s" %(rel.name.id,rel.supplier_id.id) )
            ids = [x[0] for x in cr.fetchall()]
            self.pool.get('product.supplierinfo').unlink(cr,uid,ids,context)
        return True

#   cr.execute('select name, supplier_id from library_editor_supplier where id in ('+','.join(map(str,ids))+')' )


    def write(self, cr, user, ids, vals, context={}):
        raise osv.except_osv("Warning","Only creation and suppression are allowed in this form.")

library_editor_supplier()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

