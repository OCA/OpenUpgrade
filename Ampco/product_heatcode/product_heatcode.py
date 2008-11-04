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
import netsvc
from osv import fields, osv
import ir


class properties_details(osv.osv):
    _name="properties.details"
    _description="Properties"
    _columns={
          'code': fields.char('Code',size=2,required=True,select=True),
          'name' : fields.char('Name',size=100,select=True,required=True),
          'description' : fields.char('Desciption',size=256),
          'property_type': fields.selection([('phy','Physical'),
                                             ('che','Chemical'),
#                                             ('the','Thermal'),
#                                             ('mech','Mechanical'),
#                                             ('ele','Electrical'),
                                             ],'Property Type',select=True)
      }

properties_details()

class product_heatcode(osv.osv):
    _name="product.heatcode"
    _description="Product HeatCode"
    _columns={
          'heatcode' : fields.char("HeatCode",size=50,select=True),
          'product_id' : fields.many2one('product.product','Product',required=True,select=True),
          'product_property' : fields.one2many('product.properties','heatcode_id','Property Values'),
      }

    _sql_constraints = [
        ('heatcode_uniq', 'unique (heatcode)', 'The heatcode for the product must be unique !')
    ]


product_heatcode()


class product_properties(osv.osv):
    _name="product.properties"
    _description="Product's Properties"
    _columns={
          'heatcode_id' : fields.many2one('product.heatcode','HeatCode',ondelete='cascade',required=True,select=True),
          'property_id' : fields.many2one('properties.details','Property',required=True,select=True),
          'value' : fields.float('Value',digits=(16,2)),
          'comments':fields.char("Comments",size=100),
      }

product_properties()


#class product_heatcode(osv.osv):
#    _name="product.heatcode"
#    _description="Product HeatCode"
#    _columns={
#       'id' : fields.integer('Heatcode',required=True),
#       'product_id':fields.one2many('product.product','product_id','Product Name'),
#       'product_properties' :fields.
#      }


#class chemical_properties(osv.osv):
#    _name="chemical.properties"
#    _description="Chemical Properties of Product"
#    _columns={
#          'code': fields.char('Code',size=2,required=True,select=True),
#          'description' : fields.char('Desciption',size=100,select=True,required=True),
#      }
#chemical_properties()
#
#class mechanical_properties(osv.osv):
#    _name="mechanical.properties"
#    _description="Mechanical Properties of Product"
#    _columns={
#          'code': field.char('Code',size=2,required=True,select=True),
#          'name' : field.char('Name',size=100,select=True,required=True),
#          'description' : field.char('Desciption',size=256,select=True,required=True),
#      }
#mechanical_properties()
#
#
#class thermal_properties(osv.osv):
#    _name="thermal.properties"
#    _description="Theraml Properties of Product"
#    _columns={
#          'code': field.char('Code',size=2,required=True,select=True),
#          'name' : field.char('Name',size=100,select=True,required=True),
#          'description' : field.char('Desciption',size=256,select=True,required=True),
#      }
#thermal_properties()
#
#class electrical_properties(osv.osv):
#    _name="electrical.properties"
#    _description="Electrical Properties of Product"
#    _columns={
#          'code': field.char('Code',size=2,required=True,select=True),
#          'name' : field.char('Name',size=100,select=True,required=True),
#          'description' : field.char('Desciption',size=256,select=True,required=True),
#      }
#electrical_properties()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

