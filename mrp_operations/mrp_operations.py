##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: mrp.py 1292 2005-09-08 03:26:33Z pinky $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields
from osv import osv
import ir

import netsvc
import time
from mx import DateTime

#----------------------------------------------------------
# Workcenters
#----------------------------------------------------------
# capacity_hour : capacity per hour. default: 1.0.
#          Eg: If 5 concurrent operations at one time: capacity = 5 (because 5 employees)
# unit_per_cycle : how many units are produced for one cycle
#
# TODO: Work Center may be recursive ?
#

class mrp_production_workcenter_line(osv.osv):
	_inherit = 'mrp.production.workcenter.line'
	_name = 'mrp.production.workcenter.line'
	_description = 'Production workcenters used'

	def _calc_delay(self, cr, uid, ids, name, arg, context={}):
		result = {}
		for obj in self.browse(cr, uid, ids, context):
			if obj.date_start and obj.date_finnished:
				diff = DateTime.strptime(obj.date_finnished, '%Y-%m-%d %H:%M:%S') - DateTime.strptime(obj.date_start, '%Y-%m-%d %H:%M:%S')
				result[obj.id]=diff.day
			else:
				result[obj.id] = 0
		return result

	_columns = {
		'state': fields.selection([('draft','Draft'),('confirm', 'Confirm'),('cancel','Canceled'),('done','Done')],'State', readonly=True),
		'date_start': fields.datetime('Start Date'),
		'date_finnished': fields.datetime('End Date'),
		'delay': fields.function(_calc_delay, method=True, type='integer', string='Delay', help="This is delay between operation start and stop in this workcenter"),

	}
	_defaults = {
		'state': lambda *a: 'draft',
	}

	def action_draft(self, cr, uid, ids):
		self.write(cr, uid, ids, {'state':'draft','date_start':None})
		return True

	def action_confirm(self, cr, uid, ids):
		self.write(cr, uid, ids, {'state':'confirm','date_start':DateTime.now().strftime('%Y-%m-%d %H:%M:%S')})
		return True

	def action_done(self, cr, uid, ids):
		self.write(cr, uid, ids, {'state':'done','date_finnished':DateTime.now().strftime('%Y-%m-%d %H:%M:%S')})
		return True

	def action_cancel(self, cr, uid, ids):
		self.write(cr, uid, ids, {'state':'cancel','date_start':None})
		return True

mrp_production_workcenter_line()

class mrp_production(osv.osv):
	_name = 'mrp.production'
	_inherit = 'mrp.production'
	_description = 'Production'

	def action_confirm(self, cr, uid, ids):
		obj=self.browse(cr,uid,ids)[0]
		for workcenter_line in obj.workcenter_lines:
			tmp=self.pool.get('mrp.production.workcenter.line').action_confirm(cr,uid,[workcenter_line.id])
		return super(mrp_production,self).action_confirm(cr,uid,ids)

	def action_production_end(self, cr, uid, ids):
		obj=self.browse(cr,uid,ids)[0]
		for workcenter_line in obj.workcenter_lines:
			tmp=self.pool.get('mrp.production.workcenter.line').action_done(cr,uid,[workcenter_line.id])
		return super(mrp_production,self).action_production_end(cr,uid,ids)

	def action_cancel(self, cr, uid, ids):
		obj=self.browse(cr,uid,ids)[0]
		for workcenter_line in obj.workcenter_lines:
			tmp=self.pool.get('mrp.production.workcenter.line').action_cancel(cr,uid,[workcenter_line.id])
		return super(mrp_production,self).action_cancel(cr,uid,ids)

mrp_production()