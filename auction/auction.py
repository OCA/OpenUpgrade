##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#					Fabien Pinckaers <fp@tiny.Be>
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

import time
import netsvc
from osv import fields, osv, orm
import ir

#----------------------------------------------------------
# Auction Artists
#----------------------------------------------------------
class auction_artists(osv.osv):
	_name = "auction.artists"
	_columns = {
		'name': fields.char('Artist/Author Name', size=64, required=True),
		'pseudo': fields.char('Pseudo', size=64),
		'birth_death_dates':fields.char('Birth / Death dates',size=64),
		'biography': fields.text('Biography', required=False),
	}
auction_artists()

#----------------------------------------------------------
# Auction Dates
#----------------------------------------------------------
class auction_dates(osv.osv):
	_name = "auction.dates"

	def _adjudication_get(self, cr, uid, ids, prop, unknow_none,unknow_dict):
		tmp={}
		for id in ids:
			tmp[id]=0.0
			cr.execute("select sum(obj_price) from auction_lots where auction_id=%d", (id,))
			sum = cr.fetchone()
			if sum:
				tmp[id]=sum[0]
		return tmp

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['name', 'expo1'], context)
		name = [(r['id'],'['+r['expo1']+'] '+ r['name']) for r in reads]
		return name

	_columns = {
		'name': fields.char('Auction date', size=64, required=True),
		'expo1': fields.date('First Exposition Day', required=True),
		'expo2': fields.date('Last Exposition Day', required=True),
		'auction1': fields.date('First Auction Day', required=True),
		'auction2': fields.date('Last Auction Day', required=True),
		'journal_id': fields.many2one('account.journal', 'Journal', required=True),
		'buyer_costs': fields.many2many('account.tax', 'auction_buyer_taxes_rel', 'auction_id', 'tax_id', 'Buyer Costs'),
		'seller_costs': fields.many2many('account.tax', 'auction_seller_taxes_rel', 'auction_id', 'tax_id', 'Seller Costs'),
		'acc_income': fields.many2one('account.account', 'Income Account', required=True),
		'acc_expense': fields.many2one('account.account', 'Expense Account', required=True),
		#'acc_refund': fields.many2one('account.account', 'Refund Account', required=True),
		'adj_total': fields.function(_adjudication_get, method=True, string='Total Adjudication',store=True),
		'journal_id': fields.many2one('account.journal', 'Journal', required=True),
		'state': fields.selection((('draft','Draft'),('sold','Closed')),'State',required=True),
		#'state': fields.selection((('draft','Draft'),('close','Closed')),'State', readonly=True),
		'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', required=True),
	}
	_defaults = {
		#'state': lambda uid, page, ref: 'draft'
		'state': lambda *a: 'draft',
	}
	_order = "auction1 desc"

	def close(self, cr, uid, ids, *args):
		"""
		Close an auction date.

		Create invoices for all buyers and sellers.
		STATE = unsold instead of 'close'

		RETURN: True
		"""
		cr.execute('select count(*) as c from auction_lots where auction_id in ('+','.join(map(str,ids))+') and state=%s and obj_price>0 and ach_uid is null and obj_price is not null', ('draft',))
		nbr = cr.fetchone()[0]
		if nbr>0:
			cr.execute('select * from auction_lots where auction_id in ('+','.join(map(str,ids))+') and state=%s and obj_price>0 and ach_uid is null and obj_price is not null', ('draft',))
			raise orm.except_orm('UserError', ('Please assign all buyer before closing the auction !', 'init'))
		ach_uids = {}
		cr.execute('select ach_uid,id from auction_lots where auction_id in ('+','.join(map(str,ids))+') and state=%s and obj_price>0', ('draft',))
		for arg in cr.fetchall():
			if arg[0] not in ach_uids:
				ach_uids[arg[0]]=[]
			ach_uids[arg[0]].append(arg[1])
		for arg in ach_uids:
			self.pool.get('auction.lots').lots_invoice(cr, uid, ach_uids[arg], arg)
		cr.execute('update auction_lots set obj_price=0.0 where obj_price is null and auction_id in ('+','.join(map(str,ids))+')')
		cr.execute('update auction_lots set state=%s where state=%s and auction_id in ('+','.join(map(str,ids))+')', ('draft','unsold'))
		cr.execute('select * from auction_lots where auction_id in ('+','.join(map(str,ids))+') and obj_price>0')
		ids2 = [x[0] for x in cr.fetchall()]
		self.pool.get('auction.lots').seller_trans_create(cr, uid, ids2)
		self.write(cr, uid, ids, {'state':'unsold'})
		return True

auction_dates()


#----------------------------------------------------------
# Deposits
#----------------------------------------------------------
def _inv_uniq(cr, ids):
	cr.execute('select name from auction_deposit where id in ('+','.join(map(lambda x: str(x), ids))+')')
	for datas in cr.fetchall():
		cr.execute('select count(*) from auction_deposit where name=%s', (datas[0],))
		if cr.fetchone()[0]>1:
			return False
	return True

class auction_deposit(osv.osv):
	_name = "auction.deposit"
	_description="Deposit Border"
	_columns = {

		'image': fields.binary('Image'),
		'name': fields.char('Depositer Inventory', size=64, required=True),
		'partner_id': fields.many2one('res.partner', 'Seller', required=True, change_default=True),
		'date_dep': fields.date('Deposit date', required=True),
		'method': fields.selection((('keep','Keep until sold'),('decease','Decrease limit of 10%'),('contact','Contact the Seller')), 'Withdrawned method', required=True),
		'tax_id': fields.many2one('account.tax', 'Expenses'),
		'info': fields.char('Description', size=64),
		'lot_id': fields.one2many('auction.lots', 'bord_vnd_id', 'Objects'),
		'specific_cost_ids': fields.one2many('auction.deposit.cost', 'deposit_id', 'Specific Costs'),
		'total_neg': fields.boolean('Allow Negative Amount'),

	}
	_defaults = {
		'date_dep': lambda *a: time.strftime('%Y-%m-%d'),
		'method': lambda *a: 'keep',
		'total_neg': lambda *a: False,
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'auction.deposit'),
	}
	_constraints = [
	#	(_inv_uniq, 'Twice the same inventory number !', ['name'])
	]
	def partner_id_change(self, cr, uid, ids, part):
		return {}
auction_deposit()

#----------------------------------------------------------
# (Specific) Deposit Costs
#----------------------------------------------------------
class auction_deposit_cost(osv.osv):
	_name = 'auction.deposit.cost'
	_columns = {
		'name': fields.char('Cost Name', required=True, size=64),
		'amount': fields.float('Amount'),
		'account': fields.many2one('account.account', 'Destination Account', required=True),
		'deposit_id': fields.many2one('auction.deposit', 'Deposit'),
	}
auction_deposit_cost()

#----------------------------------------------------------
# Lots Categories
#----------------------------------------------------------
class auction_lot_category(osv.osv):
	_name = 'auction.lot.category'
	_columns = {
		'name': fields.char('Category Name', required=True, size=64),
		'priority': fields.float('Priority'),
		'active' : fields.boolean('Active'),
		'aie_categ' : fields.selection([('41',"Unclassifieds"),
			('2',"Antiques"),
			('42',"Antique/African Arts"),
			('59',"Antique/Argenterie"),
			('45',"Antique/Art from the Ivory Coast"),
			('46',"Antique/Art from the Ivory Coast/African Arts"),
			('12',"Antique/Books, manuscripts, eso."),
			('11',"Antique/Carpet and textilles"),
			('14',"Antique/Cartoons"),
			('26',"Antique/Clocks and watches"),
			('31',"Antique/Collectible & art objects"),
			('33',"Antique/Engravings"),
			('10',"Antique/Furnitures"),
			('50',"Antique/Graphic Arts"),
			('37',"Antique/Jewelry"),
			('9',"Antique/Lightings"),
			('52',"Antique/Metal Ware"),
			('51',"Antique/Miniatures / Collections"),
			('53',"Antique/Musical Instruments"),
			('19',"Antique/Old weapons and militaria"),
			('43',"Antique/Oriental Arts"),
			('47',"Antique/Oriental Arts/Chineese furnitures"),
			('24',"Antique/Others"),
			('8',"Antique/Painting"),
			('25',"Antique/Porcelain, Ceramics, Glassmaking, ..."),
			('13',"Antique/Posters"),
			('56',"Antique/Religiosa"),
			('54',"Antique/Scientific Instruments"),
			('18',"Antique/Sculpture, bronze, eso."),
			('55',"Antique/Tin / Copper wares"),
			('16',"Antique/Toys"),
			('57',"Antique/Verreries"),
			('17',"Antique/Wine"),
			('1',"Contemporary Art"),
			('58',"Cont. Art/Arts"),
			('27',"Cont. Art/Curiosa"),
			('15',"Cont. Art/Jewelry"),
			('30',"Cont. Art/Other Media"),
			('3',"Cont. Art/Photo"),
			('4',"Cont. Art/Painting"),
			('5',"Cont. Art/Sculpture"),
			('48',"Cont. Art/Shows")],
			'Aie Category'),
	}
	_defaults = {
		'active' : lambda *a: 1,
		'aie_categ' : lambda *a:1,
	}
auction_lot_category()

def _type_get(self, cr, uid,ids):
	cr.execute('select name, name from auction_lot_category order by name')
	return cr.fetchall()

#----------------------------------------------------------
# Lots
#----------------------------------------------------------
def _inv_constraint(cr, ids):
	cr.execute('select id, bord_vnd_id, lot_num from auction_lots where id in ('+','.join(map(lambda x: str(x), ids))+')')
	for datas in cr.fetchall():
		cr.execute('select count(*) from auction_lots where bord_vnd_id=%s and lot_num=%s', (datas[1],datas[2]))
		if cr.fetchone()[0]>1:
			return False
	return True

class auction_lots(osv.osv):
	_name = "auction.lots"
	_order = "obj_num,lot_num"
	_description="Object"


	def button_not_bought(self,cr,uid,ids,*a):
		lots=self.browse(cr,uid,ids)
		for lot in lots:
			self.write(cr,uid,[lot.id], {'state':'unsold'})	
		return True
	def button_bought(self,cr,uid,ids,*a):
		lots=self.browse(cr,uid,ids)
		for lot in lots:
			self.write(cr,uid,[lot.id], {'state':'sold'})	
		return True
	def _buyerprice(self, cr, uid, ids, name, args, context):
		res={}
		auction_lots_obj = self.read(cr,uid,ids,['obj_price','auction_id'])

		for auction_data in auction_lots_obj:
			total_tax = 0.0
			if auction_data['auction_id']:
				auction_dates = self.pool.get('auction.dates').read(cr,uid,[auction_data['auction_id'][0]],['buyer_costs'])[0]
				if auction_dates['buyer_costs']:
					account_taxes = self.pool.get('account.tax').read(cr,uid,auction_dates['buyer_costs'],['amount'])
					for acc_amount in account_taxes:
						total_tax += acc_amount['amount']
			res[auction_data['id']] = auction_data['obj_price'] + total_tax
		return res
	def _sellerprice(self, cr, uid, ids, name, args, context):
		res={}
		auction_lots_obj = self.read(cr,uid,ids,['obj_price','auction_id'])
		for auction_data in auction_lots_obj:
			total_tax = 0.0
			if auction_data['auction_id']:
				auction_dates = self.pool.get('auction.dates').read(cr,uid,[auction_data['auction_id'][0]],['seller_costs'])[0]
				if auction_dates['seller_costs']:
					account_taxes = self.pool.get('account.tax').read(cr,uid,auction_dates['seller_costs'],['amount'])
					for acc_amount in account_taxes:
						total_tax += acc_amount['amount']
			res[auction_data['id']] = auction_data['obj_price'] - total_tax
		return res
	def _grossprice(self, cr, uid, ids, name, args, context):
		res={}
		auction_lots_obj = self.read(cr,uid,ids,['seller_price','buyer_price','auction_id'])
		for auction_data in auction_lots_obj:
			total_tax = 0.0
			if auction_data['auction_id']:
				total_tax += auction_data['buyer_price']-auction_data['seller_price']
			res[auction_data['id']] = total_tax
		return res
	def _grossmargin(self, cr, uid, ids, name, args, context):
		res={}
		auction_lots_obj = self.read(cr,uid,ids,['gross_revenue','auction_id'])

		for auction_data in auction_lots_obj:
			total_tax = 0.0
			if auction_data['auction_id']:
				auction_dates = self.pool.get('auction.dates').read(cr,uid,[auction_data['auction_id'][0]],['adj_total'])[0]
				if auction_dates['adj_total']:
						total_tax += (auction_data['gross_revenue']*100)/auction_dates['adj_total']
			res[auction_data['id']] =  total_tax
		return res
	def _netmargin(self, cr, uid, ids, name, args, context):
		res={}
		auction_lots_obj = self.read(cr,uid,ids,['net_revenue','auction_id'])

		for auction_data in auction_lots_obj:
			total_tax = 0.0
			if auction_data['auction_id']:
				auction_dates = self.pool.get('auction.dates').read(cr,uid,[auction_data['auction_id'][0]],['adj_total'])[0]
				if auction_dates['adj_total']:
						total_tax += (auction_data['net_revenue']*100)/auction_dates['adj_total']
			res[auction_data['id']] =  total_tax
		return res
	def _costs(self,cr,uid,ids,context,*a):
		"""
		costs: Total credit of analytic account 
		/ # objects sold during this auction 
		(excluding analytic lines that are in the analytic journal of the auction date).
		"""
		res={}
		som=0.0
		for lot in self.browse(cr,uid,ids):
			auct_id=lot.auction_id
			nb=cr.execute('select count(*) from auction_lots where state=%s and auction_id=%d', ('paid',auct_id))
			account_analytic_line_obj = self.pool.get('account.analytic.line')
			line_ids = account_analytic_line_obj.search(cr, uid, [('account_id', '=', lot.auction_id.account_analytic_id.id),('journal_id', '<>', lot.auction_id.journal_id.id)])
			for line in line_ids:
				som+=line.amount
			if nb>0: res[lot.id]=som/nb
			else: res[lot.id]= 0
		return res

	def _netprice(self, cr, uid, ids, name, args, context):
		res={}
		auction_lots_obj = self.read(cr,uid,ids,['seller_price','buyer_price','auction_id','costs'])
		for auction_data in auction_lots_obj:
			total_tax = 0.0
			if auction_data['auction_id']:
				total_tax += auction_data['buyer_price']-auction_data['seller_price']-auction_data['costs']
			res[auction_data['id']] = total_tax
		return res
	
	def _is_paid_vnd(self,cr,uid,ids,*a):
		res = {}
		lots=self.browse(cr,uid,ids)
		for lot in lots:
			res[lot.id] = False
			if lot.sel_inv_id:
				if lot.sel_inv_id.state == 'paid':
					res[lot.id] = True
		return res
	def _is_paid_ach(self,cr,uid,ids,*a):
		res = {}
		lots=self.browse(cr,uid,ids)
		for lot in lots:
			res[lot.id] = False
			if lot.ach_inv_id:
				if lot.ach_inv_id.state == 'paid':
					res[lot.id] = True
		return res
	_columns = {
		'bid_lines':fields.one2many('auction.bid_line','lot_id', 'Bids'),
		'auction_id': fields.many2one('auction.dates', 'Auction Date', required=True),
		'bord_vnd_id': fields.many2one('auction.deposit', 'Depositer Inventory', required=True),
		'name': fields.char('Short Description',size=64, required=True),
		'name2': fields.char('Short Description (2)',size=64),
		'lot_type': fields.selection(_type_get, 'Object Type', size=64),
		'author_right': fields.many2one('account.tax', 'Author rights'),
		'lot_est1': fields.float('Minimum Estimation'),
		'lot_est2': fields.float('Maximum Estimation'),
		'lot_num': fields.integer('List Number', required=True, ),
		'history_ids':fields.one2many('auction.lot.history', 'lot_id', 'Auction history'),
		'lot_local':fields.char('Location',size=64),
		'artist_id':fields.many2one('auction.artists', 'Artist/Author'),
		'artist2_id':fields.many2one('auction.artists', 'Artist/Author 2'),
		'important':fields.boolean('To be Emphatized'),
		'product_id':fields.many2one('product.product', 'Product', required=True),
		'obj_desc': fields.text('Object Description'),
		'obj_num': fields.integer('Catalog Number'),
		'obj_ret': fields.float('Price retired'),
		'obj_comm': fields.boolean('Commission'),
		'obj_price': fields.float('Adjudication price'),
		'ach_avance': fields.float('Buyer Advance'),
		'ach_login': fields.char('Buyer Username',size=64),
		'ach_uid': fields.many2one('res.partner', 'Buyer'),
		'ach_emp': fields.boolean('Taken Away'),
		'ach_inv_id': fields.many2one('account.invoice','Buyer Invoice', readonly=True, states={'draft':[('readonly',False)]}),
		'sel_inv_id': fields.many2one('account.invoice','Seller Invoice', readonly=True, states={'draft':[('readonly',False)]}),
		'vnd_lim': fields.float('Seller limit'),
		'vnd_lim_net': fields.boolean('Net limit ?'),
		'image': fields.binary('Image'),
		'paid_vnd':fields.function(_is_paid_vnd,string='Buyer Paid',method=True,type='boolean'),
		'paid_ach':fields.function(_is_paid_ach,string='Seller Paid',method=True,type='boolean'),
		'state': fields.selection((('draft','Draft'),('unsold','Unsold'),('paid','Paid'),('sold','Sold')),'State', required=True, readonly=True),
		'buyer_price': fields.function(_buyerprice, method=True, string='Buyer price',store=True),
		'seller_price': fields.function(_sellerprice, method=True, string='Seller price',store=True),
		'gross_revenue':fields.function(_grossprice, method=True, string='Gross revenue',store=True),
		'net_revenue':fields.function(_netprice, method=True, string='Net revenue',store=True),
		'gross_margin':fields.function(_grossmargin, method=True, string='Gross Margin',store=True),
		'net_margin':fields.function(_netmargin, method=True, string='Net Margin',store=True),
		'costs':fields.function(_costs,method=True,string='Costs',store=True),

	}
	_defaults = {
		'state':lambda *a: 'draft',
		'lot_num':lambda *a:1

	}
	_constraints = [
#		(_inv_constraint, 'Twice the same inventory number !', ['lot_num','bord_vnd_id'])
	]

	def name_get(self, cr, user, ids, context={}):
		if not len(ids):
			return []
		result = [ (r['id'], str(r['obj_num'])+' - '+r['name']) for r in self.read(cr, user, ids, ['name','obj_num'])]
		return result

	def name_search(self, cr, user, name, args=[], operator='ilike', context={}):
		ids = self.search(cr, user, [('name',operator,name)]+ args)
		ids += self.search(cr, user, [('obj_num','=',int(name))]+ args)
		return self.name_get(cr, user, ids)

	def _sum_taxes_by_type_and_id(self, taxes):
		"""
		PARAMS: taxes: a list of dictionaries of the form {'id':id, 'amount':amount, ...}
		RETURNS	: a list of dictionaries of the form {'id':id, 'amount':amount, ...}; one dictionary per unique id.
			The others fields in the dictionaries (other than id and amount) are those of the first tax with a particular id.
		"""
		taxes_summed = {}
		for tax in taxes:
			key = (tax['type'], tax['id'])
			if key in taxes_summed:
				taxes_summed[key]['amount'] += tax['amount']
			else:
				taxes_summed[key] = tax

		return taxes_summed.values()

	def compute_buyer_costs(self, cr, uid, ids):
		lots = self.browse(cr, uid, ids)
##CHECKME: est-ce que ca vaudrait la peine de faire des groupes de lots qui ont les memes couts pour passer des listes de lots a compute?
		taxes = []
		amount_total=0.0
	#	pt_tax=pool.get('account.tax')
		for lot in lots:
			taxes = lot.product_id.taxes_id
			if lot.bord_vnd_id.tax_id:
				taxes.append(lot.author_right)
			else:
				taxes += lot.auction_id.buyer_costs
			tax=self.pool.get('account.tax').compute(cr,uid,taxes,lot.obj_price,1)
			for t in tax:
				amount_total+=t['amount']
			amount_total+=lot.obj_price

		return amount_total		



#		for t in taxes_res:
#			t.update({'type': 0})
#		return self._sum_taxes_by_type_and_id(taxes_res)

#	lots=self.browse(cr,uid,ids)
#	amount=0.0
#	for lot in lots:
#		taxes=lot.product_id.taxe_id
			

	def _compute_lot_seller_costs(self, cr, uid, lot, manual_only=False):
		costs = []

		tax_cost_ids = [i.id for i in lot.auction_id.seller_costs]

		# if there is a specific deposit cost for this depositer, add it
		border_id = lot.bord_vnd_id
		if border_id:
			if border_id.tax_id:
				tax_cost_ids.append(border_id.tax_id.id)
		tax_costs = self.pool.get('account.tax').compute(cr, uid, tax_cost_ids, lot.obj_price, 1)

		# delete useless keys from the costs computed by the tax object... this is useless but cleaner...
		for cost in tax_costs:
			del cost['account_paid_id']
			del cost['account_collected_id']

		if not manual_only:
			costs.extend(tax_costs)
			for c in costs:
				c.update({'type': 0})

		if lot.vnd_lim_net and lot.obj_price>0:
#FIXME: la string 'remise lot' devrait passer par le systeme de traductions
			obj_price_wh_costs = reduce(lambda x, y: x + y['amount'], tax_costs, lot.obj_price)
			if obj_price_wh_costs < lot.vnd_lim:
				costs.append({	'type': 1,
								'id': lot.obj_num,
								'name': 'Remise lot '+ str(lot.obj_num),
								'amount': lot.vnd_lim - obj_price_wh_costs}
								#'account_id': lot.auction_id.acc_refund.id
							)
		return costs
	def compute_seller_costs(self, cr, uid, ids, manual_only=False):
		lots = self.browse(cr, uid, ids)
		costs = []

		# group objects (lots) by deposit id
		# ie create a dictionary containing lists of objects
		bord_lots = {}
		for lot in lots:
			key = lot.bord_vnd_id.id
			if not key in bord_lots:
				bord_lots[key] = []
			bord_lots[key].append(lot)

		# use each list of object in turn
		for lots in bord_lots.values():
			total_adj = 0
			total_cost = 0
			for lot in lots:
				total_adj += lot.obj_price or 0.0
				lot_costs = self._compute_lot_seller_costs(cr, uid, lot, manual_only)
				for c in lot_costs:
					total_cost += c['amount']
				costs.extend(lot_costs)
			bord = lots[0].bord_vnd_id
			if bord:
				if bord.specific_cost_ids:
					bord_costs = [{'type':2, 'id':c.id, 'name':c.name, 'amount':c.amount, 'account_id':c.account} for c in bord.specific_cost_ids]
					for c in bord_costs:
						total_cost += c['amount']
					costs.extend(bord_costs)
			if (total_adj+total_cost)<0:
#FIXME: translate tax name
				new_id = bord and bord.id or 0
				c = {'type':3, 'id':new_id, 'amount':-total_cost-total_adj, 'name':'Ristourne'}#, 'account_id':lots[0].auction_id.acc_refund.id}
				costs.append(c)
		return self._sum_taxes_by_type_and_id(costs)

	# sum remise limite net and ristourne
	def compute_seller_costs_summed(self, cr, uid, ids): #ach_pay_id
		taxes = self.compute_seller_costs(cr, uid, ids)
		taxes_summed = {}
		for tax in taxes:
			if tax['type'] == 1:
				tax['id'] = 0
	#FIXME: translate tax names
				tax['name'] = 'Remise limite nette'
			elif tax['type'] == 2:
				tax['id'] = 0
				tax['name'] = 'Frais divers'
			elif tax['type'] == 3:
				tax['id'] = 0
				tax['name'] = 'Rist.'
			key = (tax['type'], tax['id'])
			if key in taxes_summed:
				taxes_summed[key]['amount'] += tax['amount']
			else:
				taxes_summed[key] = tax
		return taxes_summed.values()

	# creates the transactions between tInvoicehe auction company and the seller
	# this is done by creating a new in_invoice for each
	def seller_trans_create(self,cr, uid,ids,context):
		"""
			Create a seller invoice for each bord_vnd_id, for selected ids.
		"""

		# use each list of object in turn
		invoices = {}
		for lot in self.browse(cr,uid,ids,context):
			partner_id = lot.bord_vnd_id.partner_id.id
			if not lot.auction_id.id: return []
			else:

				if not partner_id:
					raise  orm.except_orm('No Partner for Deposit !', "The deposit border named '%s' has no partner, please set one !" % (lot.bord_vnd_id.name,))
				inv_ref=self.pool.get('account.invoice')

				if lot.obj_price>0: lot_name = lot.obj_num
				if lot.bord_vnd_id.id in invoices:
					inv_id = invoices[lot.bord_vnd_id.id]
				else:
					res = self.pool.get('res.partner').address_get(cr, uid, [lot.bord_vnd_id.partner_id.id], ['contact', 'invoice'])
					contact_addr_id = res['contact']
					invoice_addr_id = res['invoice']
					inv = {
						'name': 'Auction:' +lot.name,
						'journal_id': lot.auction_id.journal_id.id,
						'partner_id': lot.bord_vnd_id.partner_id.id,
						'type': 'in_invoice',
						}

					inv.update(inv_ref.onchange_partner_id(cr,uid, [], 'in_invoice', lot.bord_vnd_id.partner_id.id)['value'])
					inv['account_id'] = inv['account_id'] and inv['account_id'][0]
					inv_id = inv_ref.create(cr, uid, inv, context)
					inv_ref.button_compute(cr, uid, [inv_id])
					invoices[lot.bord_vnd_id.id] = inv_id

				self.write(cr,uid,[lot.id],{'sel_inv_id':inv_id,'state':'sold'})


				taxes = map(lambda x: x.id, lot.product_id.taxes_id)
				if lot.bord_vnd_id.tax_id:
					taxes.append(lot.bord_vnd_id.tax_id.id)
				else:
					taxes += map(lambda x: x.id, lot.auction_id.seller_costs)
				inv_line= {
					'invoice_id': inv_id,
					'quantity': 1,
					'product_id': lot.product_id.id,
					'name': '['+str(lot.obj_num)+'] '+lot.auction_id.name,
					'invoice_line_tax_id': [(6,0,taxes)],
					'account_analytic_id': lot.auction_id.account_analytic_id.id,
					'account_id': lot.auction_id.acc_expense.id,
					'price_unit': lot.obj_price,
					}
				self.pool.get('account.invoice.line').create(cr, uid, inv_line,context)
				#laisser l utilisateur saisir le montant total ds la facture du seller
				#wf_service = netsvc.LocalService('workflow')
				#wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)

			return invoices.values()

#	def lots_invoice_and_cancel_old_invoice(self, cr, uid, ids, invoice_number=False, buyer_id=False, action=False):
#		lots = self.read(cr, uid, ids, ['ach_inv_id'])
#
#		num_invoiced = 0
#		inv_ids = {}
#		for lot in lots:
#			if lot['ach_inv_id']:
#				inv_ids[lot['ach_inv_id'][0]] = True
#				num_invoiced += 1
#
#		if num_invoiced:
#			if not invoice_number:
#				# if some objects were already invoiced and the user didn't specify an invoice number,
#				# raise an exception
#				raise orm.except_orm('UserError', ('%d object(s) are already invoiced !' % (num_invoiced,), 'init'))
#			else:
#				wf_service = netsvc.LocalService("workflow")
#				# if the user gave an invoice number, cancel the old invoices containing
#				# the selected objects
#				for id in inv_ids:
#					wf_service.trg_validate(uid, 'account.invoice', id, 'invoice_cancel', cr)
#
#		# create a new invoice for the selected objects
#		return self.lots_invoice(cr, uid, ids, invoice_number, buyer_id, action)

	def lots_invoice(self, cr, uid, ids,context):
		"""(buyer invoice
			Create an invoice for selected lots (IDS) to BUYER_ID.
			Set created invoice to the ACTION state.
			PRE:
				ACTION:
					False: no action
					xxxxx: set the invoice state to ACTION

			RETURN: id of generated invoice
		"""
		dt = time.strftime('%Y-%m-%d')
		invoices={}
		for lot in self.browse(cr, uid, ids,context):
			partner_ref = lot.ach_uid.id
			if not lot.auction_id.id:
				return []
			else:
				if not partner_ref:
					raise orm.except_orm('Missed buyer !', 'Please fill the field buyer in the third tab.\n Or use the button "Map user" to associate a buyer to this auction !')

				inv_ref=self.pool.get('account.invoice')
				price = lot.obj_price or 0.0
				lot_name =lot.obj_num
				inv={
					'name':'Auction'+lot.name,
					'journal_id': lot.auction_id.journal_id.id,
					'partner_id': partner_ref,
					'type': 'out_invoice',}
				inv.update(inv_ref.onchange_partner_id(cr,uid, [], 'out_invoice', lot.ach_uid.id)['value'])
				inv['account_id'] = inv['account_id'] and inv['account_id'][0]
				inv_id = inv_ref.create(cr, uid, inv, context)
				inv_ref.button_compute(cr, uid, [inv_id])
				invoices[lot.bord_vnd_id.id] = inv_id
			self.write(cr,uid,[lot.id],{'ach_inv_id':inv_id,'state':'sold'})
			#calcul des taxes
			taxes = map(lambda x: x.id, lot.product_id.taxes_id)
			if lot.author_right:
				taxes.append(lot.author_right.id)
			else:
				taxes+=map(lambda x:x.id, lot.auction_id.buyer_costs)

			inv_line= {
				'invoice_id': inv_id,
				'quantity': 1,
				'product_id': lot.product_id.id,
				'name': '['+str(lot.obj_num)+'] '+ lot.auction_id.name,
				'invoice_line_tax_id': [(6,0,taxes)],
				'account_analytic_id': lot.auction_id.account_analytic_id.id,
				'account_id': lot.auction_id.acc_income.id,
				'price_unit': lot.obj_price,
				}
			self.pool.get('account.invoice.line').create(cr, uid, inv_line,context)
			wf_service = netsvc.LocalService('workflow')
			wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
		return invoices.values()

	def lots_pay(self, cr, uid, ids, buyer_id, account_id, amount):
		lots = self.browse(cr, uid, ids)
		if not len(lots):
			return True

		partner_ref = lots[0].ach_login
		auction = lots[0].auction_id
		auction_ref = auction.auction1
		account_src_id = ir.ir_get(cr,uid,[('meta','res.partner'), ('name','account.receivable')], (buyer_id or []) and [('id',str(buyer_id))] )[0][2]

#TODO: passer par le systeme de traduction
		auction_name = u'Auction ' + auction_ref + u', Part.: '+(partner_ref or '')+ u', %d lot(s)' %(len(lots),)

		transfer = {
			'name': auction_name[:60],
			'partner_id': buyer_id,
			'reference': auction_ref,
			'account_src_id': account_src_id,
			'type': 'in_payment',
			'account_dest_id': account_id,
			'amount': amount,
		}

		transfer_id = self.pool.get('account.transfer').create(cr, uid, transfer)
		self.pool.get('account.transfer').pay_validate(cr,uid,[transfer_id])
		self.write(cr, uid, ids, {'state':'paid', 'ach_pay_id':transfer_id})
		return True

	def lots_cancel_payment(self, cr, uid, ids):
		cr.execute('select id,ach_pay_id,ach_inv_id,state from auction_lots where ach_pay_id is not null and id in ('+','.join(map(str, ids))+')')
		results = cr.dictfetchall()

		pay_ids = []			# list of payment ids
		lot_invoiced_ids = []	# list of lot ids whose state is 'paid' and inv_id is not null
		lot_paid_ids = []		# list of lot ids whose state is 'paid' and inv_id is null
		not_paid_ids = []		# list of lot ids whose state is not 'paid'
		number_lot_paid = 0
		for r in results:
			if r['ach_pay_id']:
				pay_ids.append(r['ach_pay_id'])
				number_lot_paid += 1

			if r['state']=='paid':
				if r['ach_inv_id']:
					lot_invoiced_ids.append(r['id'])
				else:
					lot_paid_ids.append(r['id'])
			else:
				not_paid_ids.append(r['id'])

		if len(ids)!=number_lot_paid:
			print "Warning: not all lots were paid"

		if len(pay_ids):
			self.pool.get('account.transfer').pay_cancel(cr, uid, pay_ids)
			self.pool.get('account.transfer').unlink(cr, uid, pay_ids)

		if len(lot_paid_ids):
			self.write(cr,uid,lot_paid_ids, {'ach_pay_id':False, 'state':'draft'})
		if len(lot_invoiced_ids):
			self.write(cr,uid,lot_invoiced_ids, {'ach_pay_id':False, 'state':'invoiced'})
		if len(not_paid_ids):
			self.write(cr,uid,not_paid_ids, {'ach_pay_id':False})
		return True

	def numerotate(self, cr, uid, ids):
		cr.execute('select auction_id from auction_lots where id=%d', (ids[0],))
		auc_id = cr.fetchone()[0]
		cr.execute('select max(obj_num) from auction_lots where auction_id=%d', (auc_id,))
		try:
			max = cr.fetchone()[0]
		except:
			max = 0
		for id in ids:
			max+=1
			cr.execute('update auction_lots set obj_num=%d where id=%d', (max, id))
		return []

auction_lots()

#----------------------------------------------------------
# Auction Bids
#----------------------------------------------------------
class auction_bid(osv.osv):
	_name = "auction.bid"
	_description="Bid auctions"
	_columns = {
		'partner_id': fields.many2one('res.partner', 'Buyer Name', required=True),
		'contact_tel':fields.char('Contact',size=64),
		'name': fields.char('Bid ID', size=64,required=True),
		'auction_id': fields.many2one('auction.dates', 'Auction Date', required=True),
		'bid_lines': fields.one2many('auction.bid_line', 'bid_id', 'Bid'),
	}	
	_defaults = {
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'auction.bid'),
	}

auction_bid()

class auction_lot_history(osv.osv):
	_name = "auction.lot.history"
	_description="Lot history"
	_columns = {
		'name': fields.char('Reason',size=64),
		'lot_id': fields.many2one('auction.lots','Object', required=True, ondelete='cascade'),
		'auction_id': fields.many2one('auction.dates', 'Auction date', required=True),
		'price': fields.float('Withdrawn price', digits=(16,2))
	}
auction_lot_history()

class auction_bid_lines(osv.osv):
	_name = "auction.bid_line"
	_description="Bid"
	_columns = {
		'name': fields.char('Name',size=64),
		'bid_id': fields.many2one('auction.bid','Bid ID', required=True),
		'lot_id': fields.many2one('auction.lots','Object', required=True),
		'call': fields.boolean('To be Called'),
		'price': fields.float('Maximum Price')
	}
auction_bid_lines()

class report_buyer_auction(osv.osv):
	_name = "report.buyer.auction"
	_description = "Auction Reporting on buyer view"
	_auto = False
	_columns = {
		'buyer_login': fields.char('Buyer Login',size=64, readonly=True, select=True),
		'buyer':fields.char('Buyer',size=64, readonly=True, select=True),
		'object':fields.integer('No of objects',readonly=True, select=True),
		'total_price':fields.integer('Total price', readonly=True, select=True),
		'avg_price':fields.integer('Avg price', readonly=True, select=True),
		'date': fields.date('Create Date',  required=True),

	}

	def init(self, cr):
		cr.execute('''

 create or replace view report_buyer_auction  as
			 (select al.id,al.ach_login as "buyer_login",
			  substring(al.create_date for 10) as date,
			 rs.name as "buyer",
			 count(al.id) as "object",
			 (sum(ad.adj_total)/count(al.id)) as "total_price",
			 ((al.lot_est1+al.lot_est2)/2) as "avg_price"

		from auction_lots al,res_partner rs,auction_dates ad
		where al.ach_uid=rs.id and ad.id=al.auction_id
 group by al.ach_uid,al.ach_login,rs.name,al.id,al.lot_est1,al.lot_est2,al.buyer_price,ad.adj_total,al.create_date
			 )''')



report_buyer_auction()

class report_buyer_auction2(osv.osv):
	_name = "report.buyer.auction2"
	_description = "Auction Reporting on buyer view"
	_auto = False
	_columns = {
		'buyer_login': fields.char('Buyer Login',size=64, readonly=True, select=True),
		'buyer':fields.char('Buyer',size=64, readonly=True, select=True),
		'sumadj':fields.float('sum of adjustication',readonly=True, select=True),
		'gross_revenue':fields.float('Gross Revenue', readonly=True, select=True),
		'net_revenue':fields.float('Net Revenue', readonly=True, select=True),
		'net_margin':fields.float('Net Margin', readonly=True, select=True),
		'date': fields.date('Create Date',  required=True),

	}

	def init(self, cr):
		cr.execute('''
			create or replace view report_buyer_auction2  as
			 (select al.id,
			   substring(al.create_date for 10) as date,
			al.ach_login as "buyer_login",
			 rs.name as "buyer",
			sum(ad.adj_total) as sumadj,
			 al.gross_revenue as gross_revenue,
		 al.net_revenue as net_revenue,
			 al.net_margin as net_margin
				from auction_lots al, auction_bid ab,res_partner rs,auction_dates ad
		where al.ach_uid=rs.id and al.auction_id=ad.id group by
		al.id,al.ach_uid,al.ach_login,rs.name,ad.adj_total,
		al.gross_revenue,al.net_revenue,al.net_margin,al.create_date)''')

report_buyer_auction2()


class report_sold_object(osv.osv):

	_name='report.sold.object'
	_description = "Sold objects"
	_auto = False
	_columns = {
		'depos': fields.many2one('res.partner','Seller Name',readonly=True),
		'lot': fields.selection(_type_get, 'Object Type', size=64),
		'product_l':fields.many2one('product.product', 'Product', required=True),
		'auct_id': fields.many2one('auction.dates', 'Auction Date'),
		'lot_est1_l': fields.float('Minimum Estimation'),
		'lot_est2_l': fields.float('Maximum Estimation'),
		'artist_id_l':fields.many2one('auction.artists', 'Artist/Author'),
		'obj_desc_l': fields.text('Object Description'),
		'name_l': fields.char('Short Description',size=64, required=True),
		'obj_price_l': fields.float('Adjudication price')
		}
	def init(self, cr):
		cr.execute("""
			create or replace view report_sold_object as (
				select min(lo.id) as id,
				lo.auction_id as auct_id,
				lo.lot_type as lot,
				lo.product_id as product_l,
				lo.bord_vnd_id as depos,
				lo.lot_est1 as lot_est1_l,
				lo.lot_est2 as lot_est2_l,
				lo.artist_id as artist_id_l,
				lo.obj_desc as obj_desc_l,
				lo.name as name_l,
				lo.obj_price as obj_price_l

				  from auction_lots lo
		  where lo.state = 'sold'
	group by lo.auction_id,lo.artist_id,lo.lot_est2 ,lo.product_id,lo.bord_vnd_id,lo.lot_type,lo.obj_price,lo.lot_est1,lo.obj_desc,lo.name
				)""")
report_sold_object()


class report_seller_auction(osv.osv):
	_name = "report.seller.auction"
	_description = "Auction Reporting on seller view"
	_auto = False
	_columns = {
		'seller': fields.char('Seller Name',size=64, readonly=True, select=True),
		'object':fields.float('No of Object',readonly=True, select=True),
		'object_sold':fields.float('Object Sold',readonly=True, select=True),
		'total_price':fields.float('Total  price',readonly=True, select=True),
		'avg_price':fields.float('Avg price',readonly=True, select=True),
		'date': fields.date('Create Date',  required=True)
	   }

	def init(self, cr):
		cr.execute('''create or replace view report_seller_auction  as
			 (
			 select
			 al.id as id,
			 substring(al.create_date for 10) as date,
			 rs.name as seller,
			 count(al.id) as object,
			 (select count(al2.id) from auction_lots as al2,auction_deposit ad2
			 where ad2.id=al2.bord_vnd_id and al2.state='paid')as object_sold,
	  (sum(ade.adj_total)/count(al.id)) as "total_price",
		al.lot_est1+al.lot_est2 as avg_price

		from auction_deposit ad,res_partner rs,auction_lots al,auction_dates ade
			 where rs.id=ad.partner_id and ad.id=al.bord_vnd_id and al.auction_id=ade.id
			 group by al.id,rs.name,al.seller_price,al.lot_est1,al.lot_est2,al.create_date)''')


report_seller_auction()




class report_seller_auction2(osv.osv):
	_name = "report.seller.auction2"
	_description = "Auction Reporting on seller view2"
	_auto = False
	_columns = {
		'seller': fields.char('Seller Name',size=64, readonly=True, select=True),
		'sum_adj':fields.float('Sum Adjustication',readonly=True, select=True),
		'gross_revenue':fields.float('Gross_Revenue',readonly=True, select=True),
		'net_revenue':fields.float('Net_Revenue',readonly=True, select=True),
		'net_margin':fields.float('Net_Margin', readonly=True, select=True),
		'date': fields.date('Create Date',  required=True),


	}

	def init(self, cr):
		print "In init of auction report ..";
		cr.execute('''create or replace view report_seller_auction2  as
			 (select rs.id as id,
			substring(al.create_date for 10) as date,
			rs.name as "seller",
			sum(adt.adj_total) as "sum_adj",
			al.gross_revenue as "gross_revenue",
			al.net_revenue as "net_revenue",
			al.net_margin as "net_margin"

		from  auction_deposit ad,res_partner rs,auction_lots al,auction_dates adt
			 where rs.id=ad.partner_id and ad.id=al.bord_vnd_id and adt.id=al.auction_id
			 group by rs.id,rs.name,al.gross_revenue,al.net_revenue,al.net_margin,al.create_date)
			 ''')

report_seller_auction2()

#class report_auction_view(osv.osv):
#	_name = "report.auction.view"
#	_description = "Auction Reporting"
#	_auto = False
#	_columns = {
#		'auction': fields.char('Auction Name',size=64, readonly=True, select=True),
#		'nobjects':fields.float('No of objects',readonly=True, select=True),
#		'nbuyer':fields.float('No of buyers',readonly=True, select=True),
#		'nseller':fields.float('No of sellers',readonly=True, select=True),
#		'min_est':fields.float('Minimum Estimation', readonly=True, select=True),
#		'max_est':fields.float('Maximum Estimation', readonly=True, select=True),
#		'adj_price':fields.float('Adjudication price', readonly=True, select=True),
#		'date': fields.date('Create Date',  required=True),
#	}
#	
#	def init(self, cr):
#		cr.execute('''create or replace view report_auction_view  as
#				 (select  ad.id,
#					substring(al.create_date for 10) as date,
#					ad.name as "auction",
#					count(al.id) as "nobjects",
#					count(al.ach_uid) as "nbuyer",
#					count(al.bord_vnd_id) as "nseller",
#					al.lot_est1 as "min_est",	
#					al.lot_est2 as "max_est",
#					al.obj_price as "adj_price"
#					from auction_dates ad,auction_lots al where ad.id=al.auction_id group by
#					ad.id,ad.name,al.ach_uid,al.bord_vnd_id,al.lot_est1,al.lot_est2,al.obj_price,al.create_date)''')
#
#report_auction_view()
class report_auction_view(osv.osv):
	_name = "report.auction.view"
	_description = "Auction Reporting on view1"
	_auto = False
	_columns = {
		'auction': fields.char('Auction Name',size=64, readonly=True, select=True),
		'nobjects':fields.float('No of objects',readonly=True, select=True),
		'nbuyer':fields.float('No of buyers',readonly=True, select=True),
		'nseller':fields.float('No of sellers',readonly=True, select=True),
		'min_est':fields.float('Minimum Estimation', readonly=True, select=True),
		'max_est':fields.float('Maximum Estimation', readonly=True, select=True),
		'adj_price':fields.float('Adustication price', readonly=True, select=True),
		'date': fields.date('Create Date',  required=True)
	}

	def init(self, cr):
		cr.execute('''create or replace view report_auction_view  as
			 (select  ad.id,
			   substring(al.create_date for 10) as date,
			  ad.name as "auction",
		count(al.id) as "nobjects",
		count(al.ach_uid) as "nbuyer",
		count(al.bord_vnd_id) as "nseller",
		al.lot_est1 as "min_est",	
		al.lot_est2 as "max_est",
		al.obj_price as "adj_price"
		from auction_dates ad,auction_lots al where ad.id=al.auction_id group by
		ad.id,ad.name,al.ach_uid,al.bord_vnd_id,al.lot_est1,al.lot_est2,al.obj_price,al.create_date)''')

report_auction_view()


class report_auction_view2(osv.osv):
	_name = "report.auction.view2"
	_description = "Auction Reporting on  view2"
	_auto = False
	_columns = {
		'auction': fields.char('Auction Name',size=64, readonly=True, select=True),
		'sum_adj':fields.float('Sum of adjudication',readonly=True, select=True),
		'gross_revenue':fields.float('Gross revenue',readonly=True, select=True),
		'net_revenue':fields.float('Net revenue',readonly=True, select=True),
		'obj_margin':fields.float('Object margin', readonly=True, select=True),
		'date': fields.date('Create Date',  required=True)
	}

	def init(self, cr):
		cr.execute('''create or replace view report_auction_view2  as
			 (select  ad.id, ad.name as "auction",
			sum(ad.adj_total) as "sum_adj",
			al.gross_revenue as "gross_revenue",
			al.net_revenue as "net_revenue",
			(al.net_margin*count(al.id)) as "obj_margin"
			from auction_dates ad,auction_lots al where ad.id=al.auction_id 
			group by ad.id,ad.name,ad.adj_total,al.gross_revenue,al.net_revenue,al.net_margin)''')

report_auction_view2()

class report_buyer_auction(osv.osv):
	_name = "report.buyer.auction"
	_description = "Auction Reporting on buyer view1"
	_auto = False
	_columns = {
		'buyer_login': fields.char('Buyer Login',size=64, readonly=True, select=True),
		'buyer':fields.char('Buyer',size=64, readonly=True, select=True),
		'object':fields.integer('No of objects',readonly=True, select=True),
		'total_price':fields.integer('Total price', readonly=True, select=True),
		'avg_price':fields.integer('Avg price', readonly=True, select=True),
		'date': fields.date('Create Date',  required=True),
	}

	def init(self, cr):
		cr.execute('''
		create or replace view report_buyer_auction  as
			 (select al.id,al.ach_login as "buyer_login",
			  substring(al.create_date for 10) as date,
			 rs.name as "buyer",
			 count(al.id) as "object",
			 (sum(ad.adj_total)/count(al.id)) as "total_price",
			 ((al.lot_est1+al.lot_est2)/2) as "avg_price"
		from auction_lots al,res_partner rs,auction_dates ad
		where al.ach_uid=rs.id and ad.id=al.auction_id
 group by al.ach_uid,al.ach_login,rs.name,al.id,al.lot_est1,al.lot_est2,al.buyer_price,ad.adj_total,al.create_date
			 )''')
report_buyer_auction()

class report_buyer_auction2(osv.osv):
	_name = "report.buyer.auction2"
	_description = "Auction Reporting on buyer"
	_auto = False
	_columns = {
		'buyer_login': fields.char('Buyer Login',size=64, readonly=True, select=True),
		'buyer':fields.char('Buyer',size=64, readonly=True, select=True),
		'sumadj':fields.float('sum of adjustication',readonly=True, select=True),
		'gross_revenue':fields.float('Gross Revenue', readonly=True, select=True),
		'net_revenue':fields.float('Net Revenue', readonly=True, select=True),
		'net_margin':fields.float('Net Margin', readonly=True, select=True),
		'date': fields.date('Create Date',  required=True),

	}

	def init(self, cr):
		cr.execute('''
			create or replace view report_buyer_auction2  as
			 (select al.id,
			substring(al.create_date for 10) as date,
			al.ach_login as "buyer_login",
			rs.name as "buyer",
			sum(ad.adj_total) as sumadj,
			al.gross_revenue as gross_revenue,
			al.net_revenue as net_revenue,
			al.net_margin as net_margin
			from auction_lots al, auction_bid ab,res_partner rs,auction_dates ad
			where al.ach_uid=rs.id and al.auction_id=ad.id group by
			al.id,al.ach_uid,al.ach_login,rs.name,ad.adj_total,
			al.gross_revenue,al.net_revenue,al.net_margin,al.create_date)''')
report_buyer_auction2()

