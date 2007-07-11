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
import pooler
import sql_db

auction_move = '''<?xml version="1.0"?>
<form string="Change Auction Date">
	<group col="1" colspan="2">
	<label string="Warning, this will erase the object adjudication price and its buyer !" colspan="2"/>
	</group>
	<newline/>
	<field name="auction_id"/>
</form>'''

auction_move_fields = {
	'auction_id': {'string':'Auction Date', 'type':'many2one', 'required':True, 'relation':'auction.dates'},
}

#def _auction_move_set(self, uid, datas):
#	if datas['form']['auction_id']:
#		cr = sql_db.db.cursor()
#		cr.execute('update auction_lots set auction_id=%s, obj_price=NULL, ach_login=NULL, ach_uid=NULL, ach_pay_id=NULL, ach_inv_id=NULL, state=%s where id in ('+','.join(map(str, datas['ids']))+')', (str(datas['form']['auction_id']), 'draft'))
#		cr.execute('delete from auction_bid_line where lot_id in ('+','.join(map(str, datas['ids']))+')')
#		cr.commit()
#		cr.close()
#	return {}
def _auction_move_set(self,cr,uid,datas,context={}):
	recs = pooler.get_pool(cr.dbname).get('auction.lots')
	rec_ids = datas['ids']
	if datas['form']['auction_id'] and len(rec_ids) :
		line_ids= pooler.get_pool(cr.dbname).get('auction.bid_line').search(cr,uid,[('lot_id','in',rec_ids)])
		pooler.get_pool(cr.dbname).get('auction.bid_line').unlink(cr, uid, line_ids)
		for m in recs.history_ids:
			new_id = self.pool.get('auction.lot.history').copy(cr, uid, m.id, {'price': recs.obj_ret, 'name': 'reasons'+recs.auction_id.name})
			cr.execute('insert into auction_lots (auction_id,history_ids) values (%d,%d)', (str(datas['form']['auction_id']), new_id))
		cr.execute('update auction_lots set auction_id=%s, obj_ret=NULL, obj_price=NULL, ach_login=NULL, ach_uid=NULL,ach_inv_id=NULL,sel_inv_id=NULL,state=\'draft\' where id in ('+','.join(map(str, rec_ids))+')', (str(datas['form']['auction_id'])))
	#	cr.execute('update auction_lot_history set auction_id=%s where id in ('+','.join(map(str, rec_ids))+')', (str(datas['form']['auction_id'])))
	return {}

class wiz_auc_lots_auction_move(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch':auction_move, 'fields': auction_move_fields, 'state':[('set_date', 'Move to Auction date'),('end','Cancel')]}
		},
		'set_date': {
			'actions': [_auction_move_set],
			'result': {'type': 'state', 'state':'end'}
		}
	}

wiz_auc_lots_auction_move('auction.lots.auction_move')

