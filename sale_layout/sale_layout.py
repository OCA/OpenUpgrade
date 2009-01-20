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
from osv import fields,osv

class sale_order_line(osv.osv):

    def invoice_line_create(self, cr, uid, ids, context={}):
        new_ids=[]
        for line in self.browse(cr, uid, ids, context):
            if line.layout_type == 'article':
                new_ids.append(line.id)
        return super(sale_order_line, self).invoice_line_create(cr, uid, new_ids, context)

#    def fields_get(self, cr, uid, fields=None, context=None):
##        print 'sale layout...........................fields_get',fields
##        article = {
##            'article': [('readonly', False), ('invisible', False)],
##            'text': [('readonly', True), ('invisible', True), ('required', False)],
##            'subtotal': [('readonly', True), ('invisible', True), ('required', False)],
##            'title': [('readonly', True), ('invisible', True), ('required', False)],
##            'break': [('readonly', True), ('invisible', True), ('required', False)],
##            'line': [('readonly', True), ('invisible', True), ('required', False)],
##        }
##        states_layout = {
##            'name': {
##                'break': [('readonly', True),('required', False),('invisible', True)],
##                'line': [('readonly', True),('required', False),('invisible', True)],
##                },
##            'product_id': article,
##            'product_uom_qty': article,
##            'product_uom': article,
##            'product_uos_qty': article,
##            'product_uos': article,
##            'price_unit': article,
##            'discount': article,
##            'tax_id': article,
##            'type' : article,
##        }
#        res = super(sale_order_line, self).fields_get(cr, uid, fields, context)
#        print res
#        if 'name' in res:
#            res['name']['defaults']= 'Sub Total'
#            print '=============',res
#        return res

    def _onchange_sale_order_line_view(self, cr, uid, id, layout_type, context={}, *args):
        print '=SALE LAYYYYYYYYOUUUUTTTTTTT_onchange_sale_order_line_view',layout_type
#        temp =temp['value']= {}
#        if layout_type == 'line':
#            temp['value']['name'] = ' '
#        if layout_type == 'break':
#            temp['value']['name'] = ' '
#        if layout_type == 'subtotal':
#            temp['value']['name'] = 'Sub Total'
#            return temp
        return {}

    def create(self, cr, user, vals, context=None):
        if vals.has_key('layout_type'):
            if vals['layout_type'] == 'line':
                vals['name'] = ' '
            if vals['layout_type'] == 'break':
                vals['name'] = ' '
            if vals['layout_type'] != 'article':
                vals['product_uom_qty']= 0                
        return super(sale_order_line, self).create(cr, user, vals, context)

    def write(self, cr, user, ids, vals, context=None):
        if vals.has_key('layout_type'):
#            if vals['layout_type'] != 'article':
#                vals['product_id']= False
#                vals['product_uom_qty']= False,
#                vals['product_uom']= False,
#                vals['product_uos_qty']= False,
#                vals['product_uos']= False,
#                vals['price_unit']= False,
#                vals['discount']= False,
#                vals['tax_id']= False,
#                vals['type']= 'make_to_stock',
            if vals['layout_type'] == 'line':
                vals['name'] = ' '
            if vals['layout_type'] == 'break':
                vals['name'] = ' '
        return super(sale_order_line, self).write(cr, user, ids, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['layout_type'] = self.browse(cr, uid, id).layout_type
        return super(sale_order_line, self).copy(cr, uid, id, default, context)
    

    _name = "sale.order.line"
    _order = "order_id, sequence asc"
    _description = "Sale Order line"
    _inherit = "sale.order.line"
    _columns = {
        'layout_type': fields.selection([
                ('article','Product'),
                ('title','Title'),
                ('text','Note'),
                ('subtotal','Sub Total'),
                ('line','Separator Line'),
                ('break','Page Break'),]
            ,'Layout Type', select=True, required=True),
        'sequence': fields.integer('Sequence Number'),        
    }   

    _defaults = {
        'layout_type': lambda *a: 'article',
    }
sale_order_line()


class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
            values = {}
        res = {}
        for id in ids:
            res[id] = []
        ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',ids),('layout_type','=','article')], limit=self._limit)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            res[r[self._fields_id]].append( r['id'] )
        return res


class sale_order(osv.osv):

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['order_line'] = False
        return super(sale_order, self).copy(cr, uid, id, default, context)

    _inherit = "sale.order"
    _columns = {
        'abstract_line_ids': fields.one2many('sale.order.line', 'order_id', 'Order Lines',readonly=True, states={'draft':[('readonly',False)]}),
        'order_line': one2many_mod2('sale.order.line', 'order_id', 'Order Lines',readonly=True, states={'draft':[('readonly',False)]}),
    }
sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

