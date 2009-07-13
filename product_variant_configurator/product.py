# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 Smile.fr. All Rights Reserved
#    authors: Raphaël Valyi, Xavier Fernandez
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
from osv import fields, osv


class product_product(osv.osv):
    _inherit = "product.product"
    
    # filter only the matching variants
    def name_search(self, cr, uid, name, args=None, operator='ilike', context={}, limit=80):
        
        if context and context.get('dimension_configuration_line_ids', False):
            if not args:
                args=[]
            
            conf_lines=context.get('dimension_configuration_line_ids')
            dim_values=[ line[2]['dimension_type_value_id'] for line in conf_lines if line[2]['dimension_type_value_id']]
            constraints_list=[('dimension_value_ids', 'in', [i] ) for i in dim_values if i]
            name_contraint = []
            if name:
                name_contraint = ['|',('code','ilike',name),('name','ilike',name),('variants','ilike',name)]
            ids = self.search(cr, uid, constraints_list+args+name_contraint,context=context)
            return self.name_get(cr, uid, ids,context)

        else:
            result = super(product_product, self).name_search(cr, uid, name, args, operator, context, limit)
            return result
        
        # NOTE
        # search has not been overriden on purpose for ergonomic reasons:
        # it allows to skip the dimension filter in case of a second click on the find button
#    def search(self, cr, uid,  args=None, offset=0,  limit=2000, order=None,context={}, count=False):

product_product()
