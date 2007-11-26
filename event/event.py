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
	_name = 'event.type'
	_description= 'Event type'
	_columns = {
		'name': fields.char('Event type', size=64),
	}
event_type()

class event(osv.osv):
	_name = 'event.event'
	_description = 'Event'
	_inherits = {'crm.case.section': 'section_id'}
	_order = 'date_begin'

	def button_draft(self, cr, uid, ids, context={}):
		return self.write(cr, uid, ids, {'state':'draft'})
	def button_cancel(self, cr, uid, ids, context={}):
		return self.write(cr, uid, ids, {'state':'cancel'})
	def button_done(self, cr, uid, ids, context={}):
		return self.write(cr, uid, ids, {'state':'done'})
	def button_confirm(self, cr, uid, ids, context={}):
		return self.write(cr, uid, ids, {'state':'confirm'})

	def _get_register(self, cr, uid, ids, name, args, context=None):
		res={}
		for event in self.browse(cr, uid, ids, context):
			cr.execute('SELECT sum(nb_register) FROM crm_case WHERE section_id=%d and state in (\'open\',\'done\')',  (event.section_id.id,))
			res2 = cr.fetchone()·
			res[event.id] = res2 and res2[0] or 0
		return res

	def _get_prospect(self, cr, uid, context=None):
		res={}
		for event in self.browse(cr, uid, ids, context):
			cr.execute('SELECT sum(nb_register) FROM crm_case WHERE section_id=%d and state in (\'draft\')',  (event.section_id.id,))
			res2 = cr.fetchone()·
			res[event.id] = res2 and res2[0] or 0
		return res

	_columns = {
		'type': fields.many2one('event.type', 'Type'),
		'section_id': fields.many2one('crm.case.section', 'Case section', required=True),
		'register_max': fields.integer('Maximum Registrations'),
		'register_min': fields.integer('Minimum Registrations'),
		'register_current': fields.function(_get_register, method=True, type="integer", string='Confirmed Registrations'),
		'register_prospect': fields.function(_get_prospect, method=True, type="integer", string='Unconfirmed Registrations'),
		'project_id': fields.many2one('project.project', 'Project', readonly=True),
		'date_begin': fields.datetime('Beginning date', required=True),
		'date_end': fields.datetime('Ending date', required=True),
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done'),('cancel','Canceled')], 'State', readonly=True, required=True),
	}
	_defaults = {
		'state': lambda *args: 'draft',
		'code': lambda *args: 'Event',
		'user_id': lambda self,cr,uid,ctx: uid
	}
event()

class registration(osv.osv):
	_inherit = 'crm.case'
	_columns = {
		'nb_register': fields.integer('Number of Registration'),
	}
	_defaults = {
		'nb_register': lambda *a: 1,
	}
registration()
