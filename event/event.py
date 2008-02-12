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
			cr.execute('SELECT sum(nb_register) FROM event_registration , crm_case c WHERE c.section_id=%d and state in (\'open\',\'done\')',  (event.section_id.id,))
			res2 = cr.fetchone()
			res[event.id] = res2 and res2[0] or 0
		return res

	def _get_prospect(self, cr, uid, ids, name, args, context=None):
		res={}
		for event in self.browse(cr, uid, ids, context):
			cr.execute('SELECT sum(nb_register) FROM event_registration , crm_case c  WHERE c.section_id=%d and state in (\'draft\')',  (event.section_id.id,))
			res2 = cr.fetchone()
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

class event_registration(osv.osv):
	_name= 'event.registration'
	_description = 'Event Registration'
	_inherits = {'crm.case': 'case_id'}
	_columns = {
		'case_id':fields.many2one('crm.case','Case'),
		'nb_register': fields.integer('Number of Registration'),
	}
	_defaults = {
		'nb_register': lambda *a: 1,
	}

	def onchange_categ_id(self, cr, uid, ids, categ, context={}):
		if not categ:
			return {'value':{}}
		cat = self.pool.get('crm.case.categ').browse(cr, uid, categ, context).probability
		return {'value':{'probability':cat}}

	def onchange_partner_address_id(self, cr, uid, ids, part, email=False):
		if not part:
			return {'value':{}}
		data = {}
		if not email:
			data['email_from'] = self.pool.get('res.partner.address').browse(cr, uid, part).email
		return {'value':data}

	def _map_ids(self,method,cr, uid, ids, *args, **argv):
	   case_data = self.browse(cr,uid,ids)
	   new_ids=[]
	   for case in case_data:
	   		new_ids.append(case.case_id.id)
	   return getattr(self.pool.get('crm.case'),method)(cr, uid, new_ids, *args, **argv)

	def case_close(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_close',cr,uid,ids,*args,**argv)
 	def case_escalate(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_escalate',cr,uid,ids,*args,**argv)
	def case_open(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_open',cr,uid,ids,*args,**argv)
	def case_cancel(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_cancel',cr,uid,ids,*args,**argv)
	def case_pending(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_pending',cr,uid,ids,*args,**argv)
	def case_reset(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_reset',cr,uid,ids,*args,**argv)
 	def case_log(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_log',cr,uid,ids,*args,**argv)
	def case_log_reply(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('case_log_reply',cr,uid,ids,*args,**argv)
	def add_reply(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('add_reply',cr,uid,ids,*args,**argv)
	def remind_partner(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('remind_partner',cr,uid,ids,*args,**argv)
	def remind_user(self,cr, uid, ids, *args, **argv):
	   return self._map_ids('remind_user',cr,uid,ids,*args,**argv)


event_registration()



class report_event_registration(osv.osv):
    _name = "report.event.registration"
    _description = "Events on registrations"
    _auto = False
    _columns = {
        'name': fields.char('Event',size=20),
        'date_begin': fields.datetime('Beginning date', required=True),
        'date_end': fields.datetime('Ending date', required=True),
        'draft_state': fields.integer('Draft Registration',size=20),
        'confirm_state': fields.integer('Confirm Registration',size=20),
        'register_max': fields.integer('Maximum Registrations'),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_event_registration as (
                select
                    e.id as id,
                    (select c.name from event_event,crm_case_section c where e.section_id=c.id) as name,
                    e.date_begin as date_begin,
                    e.date_end as date_end,
                    (select count(*) from crm_case where state='draft') as draft_state ,
                    (select count(*) from crm_case where state='open') as  confirm_state,
                    e.register_max as register_max
                from
                    event_event e
            )""")
report_event_registration()



