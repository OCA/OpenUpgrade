#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osv import osv, fields
import wizard
import pooler

class city(osv.osv):

	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			return []
		res = []
		for line in self.browse(cr, uid, ids):
			state = line.state_id.name	
			country = line.state_id.country_id.name	
			location = "%s %s %s %s" %(line.zipcode, line.name, state, country)
			res.append((line['id'], location))
		return res

	def search(self, cr, uid, args=None, offset=0, limit=80, unknow=0, context=None):
		res = super(city, self).search(cr, uid, args, offset, limit, unknow, context)
		if not res and args:
			args = [('zipcode', 'ilike', args[0][2])]
			res = super(city, self).search(cr, uid, args, offset, limit, unknow, context)
		return res	
		
	_name = 'city.city'
	_description = 'City'
	_columns = {
		'state_id': fields.many2one('res.country.state', 'State', required=True, select=1),
		'name': fields.char('City', size=64, required=True, select=1),
		'zipcode': fields.char('ZIP', size=64, required=True, select=1),
	}
city()


class CountryState(osv.osv):
	_inherit = 'res.country.state'
	_columns = {
		'city_ids': fields.one2many('city.city', 'state_id', 'Cities'),
	}
CountryState()


class res_partner_address(osv.osv):	
	def _get_zip(self, cr, uid, ids, field_name, arg, context):
		res={}
		for obj in self.browse(cr,uid,ids):
			if obj.location:
				res[obj.id] = obj.location.zipcode
			else:
				res[obj.id] = ""
		return res
		
	def _get_city(self, cr, uid, ids, field_name, arg, context):
		res={}
		for obj in self.browse(cr,uid,ids):
			if obj.location:
				res[obj.id] = obj.location.name
			else:
				res[obj.id] = ""
		return res
		
	def _get_state(self, cr, uid, ids, field_name, arg, context):
		res={}
		for obj in self.browse(cr,uid,ids):
			if obj.location:
				res[obj.id] = [obj.location.state_id.id, obj.location.state_id.name]
			else:
				res[obj.id] = False
		return res

	def _get_country(self, cr, uid, ids, field_name, arg, context):
		res={}
		for obj in self.browse(cr,uid,ids):
			if obj.location:
				res[obj.id] = [obj.location.state_id.country_id.id, obj.location.state_id.country_id.name]
			else:
				res[obj.id] = False
		return res

	_inherit = "res.partner.address"
	_columns = {
			'location': fields.many2one('city.city', 'Location'),
			'zip': fields.function(_get_zip, method=True, type="char", string='Zip', size=24),
			'city': fields.function(_get_city, method=True, type="char", string='City', size=128),
			'state_id': fields.function(_get_state, obj="res.country.state", method=True, type="many2one", string='State'), 
			'country_id': fields.function(_get_country, obj="res.country" ,method=True, type="many2one", string='Country'), 
				}
res_partner_address()






