
##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

from osv import fields,osv
from osv import orm
import netsvc

class event_meeting_table(osv.osv):
	_name="event.meeting.table"
	_description="event.meeting.table"
	_columns={
		'partner_id1':fields.many2one('res.partner','First Partner',required=True),
		'partner_id2':fields.many2one('res.partner','Second Partner', required=True),
		'event_id':fields.many2one('event.event','Related Event', required=True),
		'contact_id1':fields.many2one('res.partner.contact','First Contact',required=True),
		'contact_id2':fields.many2one('res.partner.contact','Second Contact', required=True),
		'service':fields.integer('Service', required=True),
		'table':fields.char('Table',size=10,required=True),
		}
event_meeting_table()


class event_check_type(osv.osv):
	_name="event.check.type"
	_description="event.check.type"
	_columns={
		'name':fields.char('Name',size=20,required=True),
		}
event_check_type()

class event(osv.osv):

	def cci_event_fixed(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'fixed',})
		return True

	def cci_event_open(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'open',})
		return True

	def cci_event_confirm(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'confirm',})
		return True

	def cci_event_running(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'running',})
		return True

	def cci_event_done(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'done',})
		return True

	def cci_event_closed(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'closed',})
		return True

	def cci_event_cancel(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'cancel',})
		return True

	def onchange_check_type(self, cr, uid, id, type):
		if not type:
			return {}
		tmp=self.pool.get('event.type').browse(cr, uid, type)
		return {'value':{'check_type' : tmp.check_type.id}}

	def _group_names(self, cr, uid, ids):
		cr.execute('''
		SELECT distinct name
		FROM event_group
		''')
		res = cr.fetchall()
		temp=[]
		for r in res:
			temp.append((r[0],r[0]))
		return temp

	_inherit="event.event"
	_description="event.event"
	_columns={
			'state': fields.selection([('draft','Draft'),('fixed','Fixed'),('open','Open'),('confirm','Confirmed'),('running','Running'),('done','Done'),('cancel','Canceled'),('closed','Closed')], 'State', readonly=True, required=True),
			'agreement_nbr':fields.char('Agreement Nbr',size=16),
			'check_accept':fields.many2one('event.check.type','Allowed checks'),
			'mail_auto_registr':fields.boolean('Mail Auto Register',help='A mail is send when the registration is confirmed'),
			'mail_auto_confirm':fields.boolean('Mail Auto Confirm',help='A mail is send when the event is confimed'),
			'mail_registr':fields.text('Mail Register',help='Template for the mail'),
			'mail_confirm':fields.text('Mail Confirm',help='Template for the mail'),
			'note':fields.text('Note'),
			'fse_code':fields.char('FSE code',size=64),
			'fse_hours':fields.integer('FSE Hours'),
			'signet_type':fields.selection(_group_names, 'Signet type'),
			'localisation':fields.char('Localisation',size=20),
			'account_analytic_id':fields.many2one('account.analytic.account','Analytic Account'),
			'budget_id':fields.many2one('account.budget.post','Budget'),
			'product_id':fields.many2one('product.product','Product'),
			'sales_open':fields.char('Sales Open',size=20),#should be corect
			'sales_draft':fields.char('Sales Draft',size=20),#should be corect
			'check_type': fields.many2one('event.check.type','Check Type'),
			}
event()

class event_check(osv.osv):
	_name="event.check"
	_description="event.check"
	_columns={
		"name": fields.char('Name', size=128, required=True),
		"code": fields.char('Code', size=64),
		"case_id": fields.many2one('crm.case','Inscriptions',size=20),
		"state": fields.selection([('open','Open'),('block','Blocked'),('paid','Paid'),('refused','Refused'),('asked','Asked')], 'State', readonly=True),#should be check
		"unit_nbr": fields.integer('Units'),
		"type_id":fields.many2one('event.check.type','Type'),
		"date_reception":fields.date("Reception Date"),
		"date_limit":fields.date('Limit Date'),
		"date_submission":fields.date("Submission Date"),
		}
event_check()

class event_type(osv.osv):
	_inherit = 'event.type'
	_description= 'Event type'
	_columns = {
		'check_type': fields.many2one('event.check.type','Default Check Type'),
	}
event_type()

class event_group(osv.osv):
	_name= 'event.group'
	_description = 'event.group'
	_columns = {
		"name":fields.char('Group Name',size=20,required=True),
		"bookmark_name":fields.char('Value',size=128),
		"picture":fields.binary('Picture'),
#		"cavalier":fields.boolean('Cavalier',help="Check if we should print papers with participant name"),
		"type":fields.selection([('image','Image'),('text','Text')], 'Type',required=True)
		}
	_defaults = {
		'type': lambda *args: 'text',
	}

event_group()

class event_registration(osv.osv):

	def cci_event_reg_open(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'open',})
		this = self.pool.get('event.registration').browse(cr, uid, ids)
		nb = self.pool.get('event.event')._get_register( cr, uid, [this[0].event_id.id], 'register_current', args, None)
		if nb[this[0].event_id.id] >= this[0].event_id.register_min:
			wf_service = netsvc.LocalService('workflow')
			wf_service.trg_validate(uid, 'event.event', this[0].event_id.id, 'open', cr)
		return True

	def cci_event_reg_done(self, cr, uid, ids, *args):
		print 'done'
		self.write(cr, uid, ids, {'state':'done',})
		return True

	def cci_event_reg_cancel(self, cr, uid, ids, *args):
		print 'cancel'
		self.write(cr, uid, ids, {'state':'cancel',})
		return True


#	def write(self, cr, user, ids, vals, context=None):
#		print "here"
#		print vals
#		if 'state' in vals:
#			print "write"
#		return super(event_registration, self).write(cr, user, ids, vals, context=None)

#	def create(self, cr, user, vals, context=None):
#		print "create"
#		return super(event_registration, self).create(cr, user, vals, context=None)

	_inherit = 'event.registration'
	_description="event.registration"
	_columns={

			#"date_registration":fields.date('Date Registration'), available in crm.case as 'date' field
			"partner_invoice_id":fields.many2one('res.partner', 'Partner Invoice'),
			"contact_order_id":fields.many2one('res.partner.contact','Contact Order'),#should be corect,contact_order_id (onchange_contact)
			"unit_price": fields.float('Unit Price'),
			#"quantity":fields.integer('Quantity'),
			"badge_title":fields.char('Badge Title',size=128),
			"badge_name":fields.char('Badge Name',size=128),
			"badge_partner":fields.char('Badge Partner',size=128),
			"group_id": fields.many2one('event.group','Event Group'),
			"cavalier": fields.boolean('Cavalier',help="Check if we should print papers with participant name"),
			"invoice_label":fields.char("Label Invoice",size=128),
			"tobe_invoiced":fields.boolean("To be Invoice"),
			"payment_mode":fields.many2one('payment.mode',"payment mode"),#should be check (m2o ?)
			"invoice_id":fields.many2one("account.invoice","Invoice"),#should be corect
			"check_mode":fields.boolean('Check Mode'),
			"check_ids":fields.one2many('event.check','check_id',"check ids"),#should be corect (o2m ?)
			"payment_ids":fields.one2many("payment.order","pay_id","payment"),#should be corect (o2m ?)
		}

	def onchange_contact_id(self, cr, uid, ids, contact_id):
		#return name
		if not contact_id:
			return {}
		contact_data=self.pool.get('res.partner.contact').browse(cr, uid, contact_id)
		return {'value':{'badge_name' : contact_data.name,'badge_title' : contact_data.title}}

	def onchange_partner_id(self, cr, uid, ids, part, email=False):#override function for partner name.
		if not part:
			return {'value':{'partner_address_id': False}}
		addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['contact'])
		data = {'partner_address_id':addr['contact']}
		if addr['contact'] and not email:
			data['email_from'] = self.pool.get('res.partner.address').browse(cr, uid, addr['contact']).email

		partner_data=self.pool.get('res.partner').browse(cr, uid, part)
		data['badge_partner']=partner_data.name
		return {'value':data}
	def onchange_event(self, cr, uid, ids, event_id):
		if not event_id:
			return {'value':{'unit_price' : False}}
		data_event =  self.pool.get('event.event').browse(cr,uid,event_id)
		if data_event.product_id:
			return {'value':{'unit_price' : data_event.product_id.lst_price}}
		return {'value':{'unit_price' : False}}

event_registration()

class event_check(osv.osv):
	_inherit = 'event.check'
	_columns={
		"check_id" : fields.many2one('crm.case','Check Id'),
		}
event_check()

class payment_order(osv.osv):
	_inherit = 'payment.order'
	_columns={
		"pay_id" : fields.many2one('crm.case','Check Id'),
		}
payment_order()

