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

from osv import osv, fields

class mrp_characteristic_group(osv.osv):
	_name = 'mrp.characteristic.group'
	_description = 'Characteristic Group'
	_columns = {
		'name': fields.char('Characteristic Group', size=64, required=True),
		'description': fields.text('Description'),
		'axis': fields.selection([('X','X Horizontal axis'),('Y','Y Vertical axis'),('Z','Z 3rd axis'),('T','T 4th axis')], 'Prefered axis for layout'),
	}
mrp_characteristic_group()

class mrp_characteristic(osv.osv):
	_name = 'mrp.characteristic'
	_description = 'Characteristic'
	_columns = {'name': fields.char('Characteristic', size=64, required=True),
		'description': fields.text('Description'),
		'magnitude': fields.float('Magnitude'),
		'group_id': fields.many2one('mrp.characteristic.group', 'Characteristic Group', required=True),
	}
mrp_characteristic()


class product_product(osv.osv):
	_inherit = 'product.product'
	_name = 'product.product'
	_columns = {
		'characteristic_ids': fields.many2many('mrp.characteristic', 'mrp_characteristics_rel', 'product_id' ,'characteristic_id','Characteristics'),
	}

	def on_change_characteristic_ids(self,cr,uid,ids,char_ids):
		# write mod should be better?
		#char_ids=char_ids[0][2] # well, why? i dont know
		#return {'value' :{'variants':self.variant_text(cr,uid,char_ids)}}
		return {}
	def write(self, cr, uid, ids, vals, context={}):
		if 'characteristic_ids' in vals:
			text=''
			for char in self.pool.get('mrp.characteristic').browse(cr, uid, vals['characteristic_ids'][0][2]):
				text=text+'/'+char.name
			vals['variants']=text
		return super(product_product, self).write(cr, uid, ids, vals, context)
	def charact(self,cr,uid,ids,axis):
	# give the characteristic of a given axis (x,y,z or by order 1,2,3)  to have a fixed characteristics' naming
		result=[]
		for prod in self.pool.get('product.product').browse(cr, uid,ids):
			find_char=False
			count=0
			for char in prod.characteristic_ids:
				count=count+1
				if char.group_id.axis==axis or axis==count:
					find_char=char
					break
			result.append(find_char)
		return result
product_product()

class product_template(osv.osv):
	_inherit = 'product.template'
	_name = 'product.template'
	_columns = {
		'characteristic_group_ids': fields.many2many('mrp.characteristic.group', 'mrp_characteristics_group_rel','product_id' ,'characteristic_group_id','Characteristic groups'),
		'life_cycle': fields.selection([('idea','Idea or Order'),('proto','Prototype conception'),('design','Industrial design for mrp'),('cancel','Given up')], 'Life Cycle'),
		'rough_drawing': fields.binary('rough drawing'),
		'schema': fields.binary('schema'),
		'picture': fields.binary('picture'),
	}
	 
product_template()




class mrp_bom_variation(osv.osv):
	def _characteristic_group_id(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for line in self.browse(cr, uid, ids):
			res[line.id]=line.characteristic_id.group_id.name
		return res
	_name = 'mrp.bom.variation'
	_description = 'BOM characteristic variation'
	_columns = {
		'bom_id': fields.many2one('mrp.bom', 'BOM', required=True),
		'characteristic_id': fields.many2one('mrp.characteristic', 'Parent Characteristic' ),
		'product_characteristic_id': fields.many2one('mrp.characteristic', 'Component Characteristic'),
		'exclude': fields.boolean('Exclude'),
		'product_qty': fields.float('Product Qty'),
		'characteristic_group_id': fields.function(_characteristic_group_id, method=True,  type='string', string='characteristic group'),

	}

mrp_bom_variation()

def rounding(f, r):
	if not r:
		return f
	return round(f / r) * r


class mrp_bom(osv.osv):
	_inherit = 'mrp.bom'
	_name = 'mrp.bom'
	_columns = {
		'variation_lines': fields.one2many('mrp.bom.variation', 'bom_id','Variation lines'),
	}
 	def _bom_find_template(self,cr,uid,template_id,characteristics):
		# find variant of template matching characteristics
		prod_id=False
		cr.execute('select id from product_product where product_tmpl_id=%d ', (template_id,))
		ids = map(lambda x: x[0], cr.fetchall())
		for pr in self.pool.get('product.product').browse(cr, uid, ids):
			prod_id = pr.id
			if len(pr.characteristic_ids):
				for car_id in pr.characteristic_ids:
					if car_id.id not in characteristics:
						prod_id= 0
				if prod_id: 
					break
			else:
				if   not len(characteristics): # no characteristic match no characteristic 
					break
		return prod_id
	def _bom_find_variation(self,bom,characteristic,field):
		# find field value matching characteristic in variations if any
		result=False
		if bom.variation_lines:
			for var in bom.variation_lines:
				if (var.characteristic_id.id==characteristic or not(var.characteristic_id)) and var[field]:
					result=var[field]
					break
		return result
	def _bom_explode(self, cr, uid, bom, factor, properties, addthis=False, level=10,characteristics=[],qty=0):
		# new explode function for generic BOM
		factor = factor / (bom.product_efficiency or 1.0)
		factor = rounding(factor, bom.product_rounding)
		if factor<bom.product_rounding:
			factor = bom.product_rounding
		result = []
		result2 = []
		if bom.type=='phantom' and not bom.bom_lines:
			# phantom
			if  bom.product_id.characteristic_ids :
				# find generic bom and load characteristics
				newprod=self._bom_find_template(cr, uid, bom.product_id.product_tmpl_id.id,[])
				newbom= self._bom_find(cr, uid,newprod, bom.product_uom.id, properties)
				for p in bom.product_id.characteristic_ids:
					characteristics.append(p.id)						
			else:			
				newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)
			if newbom:
				res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, True, level+10,characteristics,qty)
				result = result + res[0]
				result2 = result2 + res[1]
			else:
				return [],[]
		else:
			if addthis and not bom.bom_lines: # leaf of the tree...
				prod_id=False
				# try to find a real product with same template and characteristics matching 
				if not bom.product_id.characteristic_ids and characteristics:
					prod_id=self._bom_find_template(cr, uid, bom.product_id.product_tmpl_id.id,characteristics)
				if not prod_id:
					prod_id=bom.product_id.id
				#
				result.append(
				{
					'name': bom.product_id.name,
					'product_id': prod_id,
					'product_qty': qty * factor,
					'product_uom': bom.product_uom.id,
				})
			if bom.routing_id:
				for wc_use in bom.routing_id.workcenter_lines:
					wc = wc_use.workcenter_id
					cycle = factor * wc_use.cycle_nbr
					result2.append({
						'name': bom.routing_id.name,
						'workcenter_id': wc.id,
						'sequence': level,
						'cycle': cycle,
						'hour': (wc.time_start+wc.time_stop+cycle*wc.time_cycle) * (wc.time_efficiency or 1.0),
					})
			# BOM lines
			for bom2 in bom.bom_lines:
				# 3 folowing tasks can be done in one to optimise
				#  characteristic translation
				newcharacteristics=[]
				for char in characteristics:
					v= self._bom_find_variation(bom2,char,'product_characteristic_id')
					if v:
						 newcharacteristics.append(v.id)
				#   compute qty if varying with caract.
				qty=bom2.product_qty
				for char in characteristics:
					v= self._bom_find_variation(bom2,char,'product_qty')
					if v:
						qty=v*(bom2.product_qty or 1) # if generic qty, use varition qty as a rate
				#  exclusion if matching characteristic 
				exclude=False
				for char in characteristics:
					v= self._bom_find_variation(bom2,char,'exclude')
					if v:
						exclude=True
				if not exclude:
					res = self._bom_explode(cr, uid, bom2, factor, properties, True, level+10,newcharacteristics,qty)
					result = result + res[0]
					result2 = result2 + res[1]
		 
		return result, result2
mrp_bom()

#setattr(mrp_bom(),'_std_bom_find',getattr(mrp_bom(),'_bom_find'))
#setattr(mrp_bom(),'_bom_find',getattr(mrp_bom(),'_new_bom_find'))

