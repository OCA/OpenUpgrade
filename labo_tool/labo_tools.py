##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: product_expiry.py 4304 2006-10-25 09:54:51Z ged $
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
import datetime
from osv import fields,osv
import pooler
import tools
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import wizard

class labo_tool(osv.osv):
	_name = "labo.tool"
	_description = "Labo tool Shop"
	_columns = {
		'name': fields.char('Equipment name',size=64, required=True),
		'order_tool':fields.many2one('sale.order', 'Order'),
		'log': fields.one2many('labo.log','log_id','Log'),
		'log_interv': fields.one2many('labo.intervention','intervention_id','Intervention'),
		}
	def running_expired_dates(self, cr, uid, *args):
		ref_case = pooler.get_pool(cr.dbname).get('crm.case')
		section_id=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('code', '=', 'equip'),])
		mail_admin='admin@progenus.com '
		cr.execute("""select distinct tool_id,tool_name,check_type,pdate,check_date,uid from
(
	select labo_tool.id as tool_id,labo_tool.name as tool_name, labo_intervention.id,check_in as check_type ,intervention_date as pdate,
		(case check_in
			when 'year' then intervention_date - interval '11 month'
			when 'month_6' then intervention_date - interval '5 month'
			when 'month_3' then intervention_date - interval '10 week'
			when 'month_2' then intervention_date - interval '6 week'
			when 'month_1' then intervention_date - interval '3 week'
			when 'weekly' then intervention_date - interval '6 day'
			else intervention_date
		End) as check_date,
		user_id as uid ,'Intervention' as cType
	from labo_intervention inner join labo_tool on labo_tool.id = labo_intervention.intervention_id
	union all
	select labo_tool.id as tool_id,labo_tool.name as tool_name, labo_log.id,check_in as check_type ,planified_date as pdate,
		(case check_in
			when 'year' then planified_date - interval '11 month'
			when 'month_6' then planified_date - interval '5 month'
			when 'month_3' then planified_date - interval '3 month'
			when 'month_2' then planified_date - interval '2 month'
			when 'month_1' then planified_date - interval '1 month'
			when 'weekly' then planified_date - interval '6 day'
			else null
		End) as check_date,
		user_id as uid,'Maintenance' as cType
	from labo_log inner join labo_tool on labo_tool.id = labo_log.log_id
) as tmpTable
where tmpTable.check_date = current_date
				   """)
		res = cr.dictfetchall()
		for r in res:
			partner_id= pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [r['uid']])
			new_id=ref_case.create(cr,uid,{
						'name': "Equipment to review",
						'section_id':section_id[0],
						'state': 'open',
						'active':True,
						'partner_id':partner_id[0].company_id.partner_id.id,
						'description': "Please check your reagents: " +" "+ r['tool_name'] + " for the next intervention or calibrating on " + r['check_date'][:10],
						'user_id':partner_id[0].id,
						})
			if partner_id[0].address_id and partner_id[0].address_id.email:
				tools.email_send('administrator@progenus.com',partner_id[0].address_id.email ,'Checking equipments', " for the next intervention or calibrating on " + r['check_date'], 'olivier.duterme@progenus.com', mail_admin,  tinycrm=new_id)

		return True

	def running_expired_dates3(self, cr, uid, *args):
		print "DANS RUNNING date d expiration"
		ref_case = pooler.get_pool(cr.dbname).get('crm.case')
		txt_mail="Please check your reagents:"
		print "DS RUNNIN",("select distinct(t.name),l.check_in,l.planified_date,i.check_in,i.intervention_date,i.user_id,l.user_id from labo_intervention i,labo_log l, labo_tool t  where t.id=l.log_id and i.intervention_id = t.id ")
		cr.execute("select distinct(t.name),l.check_in,l.planified_date,i.check_in,i.intervention_date,i.user_id,l.user_id from labo_intervention i,labo_log l, labo_tool t  where t.id=l.log_id and i.intervention_id = t.id ")
#cr.execute("select distinct(t.name) from labo_intervention i,labo_log l, labo_tool t  where t.id=l.log_id and i.intervention_id = t.id and (l.max_date = current_date or i.next_date = current_date) ")
		res=cr.fetchall()

		max_date= now()+ RelativeDateTime(years=+1)
		next_date= now()+ RelativeDateTime(years=+1)
		for r in res:

			if r[1] == 'year'or r[3] == 'year':
				if r[3]=='year':
					next_date = mx.DateTime.strptime(r[4], '%Y-%m-%d') +  RelativeDateTime(years=+1) + RelativeDateTime(months=-1)
				else:
					max_date = mx.DateTime.strptime(r[2], '%Y-%m-%d') +  RelativeDateTime(years=+1) + RelativeDateTime(months=-1)
			elif r[1]=='month_6' or r[3] == 'month_6':
				 if r[3]=='month_6':
					next_date = mx.DateTime.strptime(r[4], '%Y-%m-%d') +  RelativeDateTime(months=+6) + RelativeDateTime(months=-1)
				 if r[3]=='month_6':
					max_date = mx.DateTime.strptime(r[2], '%Y-%m-%d') +  RelativeDateTime(months=+6) + RelativeDateTime(months=-1)
			elif r[1]=='month_3' or r[3]=='month_3':
				if r[3]=='month_3':
					next_date = mx.DateTime.strptime(r[4], '%Y-%m-%d') +  RelativeDateTime(months=+3) + RelativeDateTime(days=-14)
				if r[1]=='month_3':
					max_date = mx.DateTime.strptime(r[2], '%Y-%m-%d') +  RelativeDateTime(months=+3) + RelativeDateTime(days=-14)
			elif r[1]=='month_2' or r[3]=='month_2':
				if r[3]=='month_2':
					next_date = mx.DateTime.strptime(r[4], '%Y-%m-%d') + RelativeDateTime(months=+2) + RelativeDateTime(days=-14)
				if r[1]=='month_2':
					max_date = mx.DateTime.strptime(r[2], '%Y-%m-%d') +  RelativeDateTime(months=+2) + RelativeDateTime(days=-14)
			elif r[1]=='month_1' or r[3]=='month_1':
				if r[3]=='month_1':
					next_date = mx.DateTime.strptime(r[4], '%Y-%m-%d') + RelativeDateTime(months=+1) + RelativeDateTime(days=-7)
				if r[1]=='month_1':
					max_date = mx.DateTime.strptime(r[2], '%Y-%m-%d') +  RelativeDateTime(months=+1) + RelativeDateTime(days=-7)
			elif r[1]=='weekly' or r[3]=='weekly' :
				if r[3]== 'weekly':
					next_date = mx.DateTime.strptime(r[4], '%Y-%m-%d') +  RelativeDateTime(days=+7) + RelativeDateTime(days=-1)
				if r[1]== 'weekly':
					max_date = mx.DateTime.strptime(r[2], '%Y-%m-%d') +  RelativeDateTime(days=+7) + RelativeDateTime(days=-1)
			if ( next_date.strftime('%Y-%m-%d') == now().strftime('%Y-%m-%d') or max_date.strftime('%Y-%m-%d') == now().strftime('%Y-%m-%d')):
				cr.execute('select distinct(current_date) from labo_intervention i,labo_tool t where t.name = %s ', (r[0],))
				next_d=([x[0] for x in cr.fetchall() if x])
				cr.execute('select distinct(current_date) from labo_log l,labo_tool t where t.id=l.log_id and t.name = %s ', (r[0],))
				max_d=([x[0] for x in cr.fetchall() if x])
				txt2="for the next intervention or calibrating"+ ",".join(([str(i) for i in next_d if i] ))
				section_id=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('code', '=', 'equip'),])

			 #   user_id=pooler.get_pool(cr.dbname).get('labo.log').search(cr,uid,[('lod' '=', '')])

				user_list=[]
				user_list.append(r[5])
				if (r[5] != r[6]):
						user_list.append(r[6])

				user_obj=pooler.get_pool(cr.dbname).get('res.users')
				mail_admin='admin@progenus.com '
				if r:
					for i in user_list:
						print "iii",i
						partner_id= pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [i])

						new_id=ref_case.create(cr,uid,{
						'name': "Equipment to review",
						'section_id':section_id[0],
						'state': 'open',
						'active':True,
						'partner_id':partner_id[0].company_id.partner_id.id,
						'description': txt_mail+ "  "+ r[0] + txt2,
						'user_id':i,
						})
						cr.execute("select r.email from res_users l, res_partner_address r  where r.id=l.address_id and l.id=%d  "%( i))
						res=cr.fetchone()[0] or ""
						print res
						address_mail=res

						if address_mail:
							tools.email_send('administrator@progenus.com',mail_admin ,'Checking equipments', txt2, 'olivier.duterme@progenus.com', address_mail,  tinycrm=new_id)
#						else:
#							raise osv.except_osv('Not Valid Email !', "Please set an email address to '%s' !" % (address_mail,))
					txt2=""
				else:
					return False
		return True


labo_tool()

class labo_log(osv.osv):
	_name = "labo.log"
#	_rec_name="planified_date"
	_description = "Labo Maintenance"
	_columns = {
		'log_id': fields.many2one('labo.tool', 'LABO TOOL', select=True),
		'user_id':fields.many2one('res.users', 'Name of operator', required=True),
		'planified_date':fields.date('Planified date'),
		'check_in': fields.selection([('year','One Year'), ('month_6','6 months'),('month_3','3 months'),('month_2','2 months'),('month_1','1 month'),('weekly','1 week')], 'Check after'),
	#	'max_date':fields.date('Max date'),
		'result_action':fields.char('Result of action',size=64),
#		'name': fields.char('Done on', size=64),
	}
labo_log()

class labo_intervention(osv.osv):
	_name = "labo.intervention"
	_description = "Labo Intervention"
	_columns = {
		'name':fields.char( 'Description of Intervention',size=64),
		'check_in': fields.selection([('year','One Year'), ('month_6','6 months'),('month_3','3 months'),('month_2','2 months'),('month_1','1 month'),('weekly','1 week')], 'Check after'),
		'intervention_id': fields.many2one('labo.tool', 'Equipment', select=True),
		'user_id':fields.many2one('res.users', 'Name of operator', required=True),
		'intervention_date':fields.date('Planified date'),
		'next_date': fields.date('Next Intervention'),
	}
labo_intervention()

