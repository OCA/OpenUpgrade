#!/usr/bin/env python
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
import wizard
import pooler

class city(osv.osv):

	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			return []
		res = []
		for line in self.browse(cr, uid, ids):
			location = line.name
			if line.zipcode:
				location = "%s %s" % (line.zipcode, location)
			if line.state_id:
				location = "%s, %s" % (location, line.state_id.name)
			if line.country_id:
				location = "%s, %s" % (location, line.country_id.name)
			res.append((line['id'], location))
		return res

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
	    if not args:
	        args = []
	    if context is None:
	        context = {}
	    ids = []
	    if name:
	        ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
	    if not ids:
	        ids = self.search(cr, user, [('zipcode', operator, name)] + args, limit=limit, context=context)
	    return self.name_get(cr, user, ids, context)
		
	_name = 'city.city'
	_description = 'City'
	_columns = {
        'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]", select=1),
		'name': fields.char('City Name', size=64, required=True, select=1),
		'zipcode': fields.char('ZIP', size=64, select=1),
        'country_id': fields.many2one('res.country', 'Country', select=1),
		'code': fields.char('City Code', size=64, help="The official code for the city"),
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
		res = {}
		for obj in self.browse(cr, uid, ids):
			if obj.location:
				res[obj.id] = obj.location.zipcode
			else:
				res[obj.id] = ""
		return res
		
	def _get_city(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for obj in self.browse(cr, uid, ids):
			if obj.location:
				res[obj.id] = obj.location.name
			else:
				res[obj.id] = ""
		return res
		
	def _get_state(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for obj in self.browse(cr, uid, ids):
			if obj.location and obj.location.state_id:
				res[obj.id] = [obj.location.state_id.id, obj.location.state_id.name]
			else:
				res[obj.id] = False
		return res

	def _get_country(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for obj in self.browse(cr, uid, ids):
			if obj.location and obj.location.country_id:
				res[obj.id] = [obj.location.country_id.id, obj.location.country_id.name]
			else:
				res[obj.id] = False
		return res

	# XXX The following search function could have been written with SQL...
	def _zip_search(self, cr, uid, obj, name, args):
		"""Search for addresses in cities with this zip code"""
		cities = self.pool.get('city.city').search(cr, uid, args=[('zipcode', args[0][1], args[0][2])])
		ids=self.search(cr, uid, args=[('location','in',cities)])
		return [('id', 'in', ids)]
	
	def _city_search(self, cr, uid, obj, name, args):
		"""Search for addresses in cities with this city name"""
		cities = self.pool.get('city.city').search(cr, uid, args=[('name', args[0][1], args[0][2])])
		ids=self.search(cr, uid, args=[('location','in',cities)])
		return [('id', 'in', ids)]

	def _state_search(self, cr, uid, obj, name, args):
		print """Search for addresses in cities in this state"""
		states = self.pool.get('res.country.state').search(cr, uid, args=[('name', args[0][1], args[0][2])])
		cities = self.pool.get('city.city').search(cr, uid, args=[('state_id', 'in', states)])
		ids=self.search(cr, uid, args=[('location','in',cities)])
		return [('id', 'in', ids)]
	
	def _country_search(self, cr, uid, obj, name, args):
		print """Search for addresses in cities in this country"""
		countries = self.pool.get('res.country').search(cr, uid, args=[('name', args[0][1], args[0][2])])
		cities = self.pool.get('city.city').search(cr, uid, args=[('country_id', 'in', countries)])
		ids=self.search(cr, uid, args=[('location','in',cities)])
		return [('id', 'in', ids)]
	
	_inherit = "res.partner.address"
	_columns = {
		'location': fields.many2one('city.city', 'Location', select=1),
		'zip': fields.function(_get_zip, method=True, type="char", string='Zip', size=24, fnct_search=_zip_search),
		'city': fields.function(_get_city, method=True, type="char", string='City', size=128, fnct_search=_city_search),
		'state_id': fields.function(_get_state, obj="res.country.state", method=True, type="many2one", string='State', fnct_search=_state_search),
		'country_id': fields.function(_get_country, obj="res.country" , method=True, type="many2one", string='Country', fnct_search=_country_search),
	}
res_partner_address()






