##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

import wizard
import netsvc

import sql_db

buyer_map = '''<?xml version="1.0"?>
<form title="Buyer Map">
	<field name="ach_login"/>
	<newline/>
	<field name="ach_uid"/>
</form>'''

buyer_map_fields = {
	'ach_login': {'string':'Buyer Username', 'type':'char', 'size':64, 'required':True},
	'ach_uid': {'string':'Buyer', 'type':'many2one', 'required':True, 'relation':'res.partner'},
}

def _buyer_map_init(self, uid, datas):
	cr = sql_db.db.cursor()
	cr.execute('select ach_login, auction_id from auction_lots where id in ('+','.join(map(str, datas['ids']))+') and (ach_uid is null) and (length(ach_login)>0) and (ach_pay_id is null) order by length(ach_login), ach_login limit 1')
	res = cr.fetchone()
	if not res:
		if datas['form'].get('done_some', False):
			raise wizard.except_wizard('Done', 'All buyers are now mapped.')
		else:
			raise wizard.except_wizard('Notice', 'All buyers for the selected objects are already mapped !')
		
	ach_login = res[0]
	ach_uid = False

	# get the id of the partner corresponding to that buyer number
	cr.execute('select id from res_partner where ref=%s', (ach_login,))
	ids = cr.fetchall()

	# if there is only one partner with that ref/buyer number, do the mapping automatically
	if len(ids)==1:
		ach_uid = ids[0][0]
	else:
		# else if there are no (or several) partner(s) matching that buyer number, look in the bids
		cr.execute('select partner_id from auction_bid where name=%s and auction_id=%d', (res[0], res[1]))
		ids = cr.fetchall()
		if len(ids)==1:
			ach_uid = ids[0][0]
	cr.close()
	return {'ach_login': ach_login, 'ach_uid': ach_uid}


def _buyer_map_set(self, uid, datas):
	if datas['form']['ach_uid'] and datas['form']['ach_login']:
		cr = sql_db.db.cursor()
		# TODO: this is a temporary fix, as is the fix in the login method
		# of service/web_services.py
		# should be fixed for all wizard, of even better, for all messages between the client and server !!!!
		# or yet even better, for all psycopg calls !!!!
		cr.execute('update auction_lots set ach_uid=%d where id in ('+','.join(map(str, datas['ids']))+') and (ach_login=%s)', (datas['form']['ach_uid'], datas['form']['ach_login'].encode('utf-8')))
		cr.commit()
		cr.close()
	return {'ach_login':'', 'ach_uid':False, 'done_some':True}

class wiz_auc_lots_buyer_map(wizard.interface):
	states = {
		'init': {
			'actions': [_buyer_map_init],
			'result': {'type': 'form', 'arch':buyer_map, 'fields': buyer_map_fields, 'state':[('set_buyer', 'Update'),('end','Exit')]}
		},
		'set_buyer': {
			'actions': [_buyer_map_set],
			'result': {'type': 'state', 'state':'init'}
		}
	}

wiz_auc_lots_buyer_map('auction.lots.buyer_map')

