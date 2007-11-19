'''Event'''
##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
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

from osv import fields, osv
import time

class event_type(osv.osv):
	_name = 'event.event_type'
	_description= 'Event type'

	_columns = {
			'name': fields.char('Event type name', size=64, required=True),
			'code': fields.char('Event type code', size=64, required=True),
			}

event_type()

class event(osv.osv):
	_name = 'event.event'
	_description = 'Event'
	_inherits = {'crm.case.section': 'section_id'}
	_order = 'date_begin asc, date_end asc'


	def _get_type(self, cr, uid, context=None):

		obj_event_type = self.pool.get('event.event_type')
		ids = obj_event_type.search(cr, uid, [])
		res = obj_event_type.read(cr, uid, ids, ['code', 'name'], context)
		return [(r['code'], r['name']) for r in res]

	def _get_register(self, cr, uid, ids, name, args, context=None):
		cr.execute('''
		SELECT r.section_id, sum(r.nb_register)
		FROM event_registration r
		WHERE r.section_id IN (%s)
		GROUP BY r.section_id
		''' % ','.join([str(i) for i in ids] )
		)

		nb_reg = dict(cr.fetchall())
		res={}
		for id in ids:
			try:
				res[id] = nb_reg[id]
			except KeyError:
				res[id] = 0
		print res
		return res

	def _get_prospect(self, cr, uid, context=None):
		return 1

	_columns = {
			'type': fields.many2one('event.event_type', 'Type', size=64, required=True),
			'section_id': fields.many2one('crm.case.section', 'Case section', required=True),
			'register_max': fields.integer('Maximum number of registrations'),
			'register_min': fields.integer('Minimum number of registrations'),
			'register_current': fields.function(_get_register, method=True, type="integer", string='Current number of registrations'),
			'register_prospect': fields.function(_get_prospect, method=True, type="integer", string='Number of prospect registrations'),
			'parent_event': fields.many2one('event.event', 'Parent event'),
			'child_events': fields.one2many('event.event', 'parent_event', 'Childs events'),
			'date_begin': fields.datetime('Beginning date', required=True),
			'date_end': fields.datetime('Ending date', required=True),
			}


event()

class registration(osv.osv):
	_name = 'event.registration'
	_description = 'Registration'
	_inherit = 'crm.case'

	_columns = {
			'nb_register': fields.integer('Number of Registration', required=True),
			'section_id': fields.many2one('event.event', 'Event', required=True, select=True),
			'name': fields.char('Description',size=64, required=False),
			'partner_id': fields.many2one('res.partner', 'Partner', required=True),
			}
	_defaults = {
			'nb_register': lambda *a: 1,
			}
registration()
