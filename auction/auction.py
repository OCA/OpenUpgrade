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

	_columns = {
		'name': fields.char('Auction date', size=64, required=True),
		'expo1': fields.date('First Exposition Day', required=True),
		'expo2': fields.date('Last Exposition Day', required=True),
		'auction1': fields.date('First Auction Day', required=True),
		'auction2': fields.date('Last Auction Day', required=True),

		'buyer_costs': fields.many2many('account.tax', 'auction_buyer_taxes_rel', 'auction_id', 'tax_id', 'Buyer Costs'),
		'seller_costs': fields.many2many('account.tax', 'auction_seller_taxes_rel', 'auction_id', 'tax_id', 'Seller Costs'),
		'acc_income': fields.many2one('account.account', 'Income Account', required=True),
		'acc_expense': fields.many2one('account.account', 'Expense Account', required=True),
		'acc_refund': fields.many2one('account.account', 'Refund Account', required=True),

		'adj_total': fields.function(_adjudication_get, method=True, string='Total Adjudication'),
		'project_id': fields.many2one('project.project', 'Project', required=True),
		'state': fields.selection((('draft','Draft'),('close','Closed')),'State', readonly=True),
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
		STATE = 'close'

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
		self.write(cr, uid, ids, {'state':'close'})
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
	_columns = {
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
		'total_neg': lambda *a: False
	}
	_constraints = [
	#	(_inv_uniq, 'Twice the same inventory number !', ['name'])
	]
	def partner_id_change(self, cr, uid, ids, part):
#CHECKME: ce truc me parait bizarre
		costs = ir.ir_get(cr,uid,[ ('meta','res.partner'), ('name','auction.seller.costs')], [('id',str(part)),('uid',str(uid))])[0][2]
		return {'value':{'expenses':costs}}
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
	_columns = {
		'bid_lines':fields.one2many('auction.bid_line','lot_id', 'Bids'),
		'auction_id': fields.many2one('auction.dates', 'Auction Date'),
		'bord_vnd_id': fields.many2one('auction.deposit', 'Depositer Inventory', required=True),
		'name': fields.char('Short Description',size=64, required=True),
		'name2': fields.char('Short Description (2)',size=64),
		'lot_type': fields.selection(_type_get, 'Object Type', size=64),
		'author_right': fields.many2one('account.tax', 'Author rights'),
		'lot_est1': fields.float('Minimum Estimation'),
		'lot_est2': fields.float('Maximum Estimation'),
		'lot_num': fields.integer('List Number', required=True),
		'lot_local':fields.char('Location',size=64),
		'artist_id':fields.many2one('auction.artists', 'Artist/Author'),
		'artist2_id':fields.many2one('auction.artists', 'Artist/Author 2'),
		'important':fields.boolean('To be Emphatized'),
		'tva':fields.many2one('account.tax', 'Tax', required=True),
		'obj_desc': fields.text('Object Description'),
		'obj_num': fields.integer('Catalog Number'),
		'obj_ret': fields.float('Price retired'),
		'obj_comm': fields.boolean('Commission'),
		'obj_price': fields.float('Adjudication price'),
		'ach_avance': fields.float('Buyer Advance'),
		'ach_login': fields.char('Buyer Username',size=64),
		'ach_uid': fields.many2one('res.partner', 'Buyer'),
		'ach_emp': fields.boolean('Taken Away'),
		'ach_pay_id': fields.many2one('account.transfer','Payment', readonly=True, states={'draft':[('readonly',False)]}),
		'ach_inv_id': fields.many2one('account.invoice','Invoice', readonly=True, states={'draft':[('readonly',False)]}),
#CHECKME: seller invoice qui pointe vers un account.move?
		'buy_inv_id': fields.many2one('account.move','Seller Invoice', readonly=True, states={'draft':[('readonly',False)]}),
		'vnd_lim': fields.float('Seller limit'),
		'vnd_lim_net': fields.boolean('Net ?'),
		'state': fields.selection((('draft','Draft'),('unsold','Unsold'),('paid','Paid'),('invoiced','Invoiced')),'State', required=True, readonly=True)
	}
	_defaults = {
				'state':lambda *a: 'draft'
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
		try:
			ids += self.search(cr, user, [('obj_num','=',int(name))]+ args)
		except ValueError, e:
			pass
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
#CHECKME: est-ce que ca vaudrait la peine de faire des groupes de lots qui ont les memes couts pour passer des listes de lots a compute?
		taxes_res = []
		for lot in lots:
			costs_ids = [c.id for c in lot.auction_id.buyer_costs]
			if lot.author_right:
				costs_ids.append(lot.author_right.id)
			taxes_res.extend(self.pool.get('account.tax').compute(cr, uid, costs_ids, lot.obj_price, 1))
		for t in taxes_res:
			t.update({'type': 0})
		return self._sum_taxes_by_type_and_id(taxes_res)

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
								'amount': lot.vnd_lim - obj_price_wh_costs,
								'account_id': lot.auction_id.acc_refund.id }
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
				c = {'type':3, 'id':new_id, 'amount':-total_cost-total_adj, 'name':'Ristourne', 'account_id':lots[0].auction_id.acc_refund.id}
				costs.append(c)
		return self._sum_taxes_by_type_and_id(costs)

	# sum remise limite net and ristourne
	def compute_seller_costs_summed(self, cr, uid, ids):
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

	# creates the transactions between the auction company and the seller
	# this is done by creating a new in_invoice for each
	def seller_trans_create(self, cr, uid, ids):
		"""
			Create a seller invoice for each bord_vnd_id, for selected ids.
		"""
		lots = self.browse(cr, uid, ids)

		# group objects (lots) by (deposit id, auction id)
		# ie create a dictionary containing lists of objects
		bord_lots = {}
		for lot in lots:
			key = (lot.bord_vnd_id.id,lot.auction_id.id)
			if not key in bord_lots:
				bord_lots[key] = []
			bord_lots[key].append(lot)

		# use each list of object in turn
		for lots in bord_lots.values():
			partner_id = lots[0].bord_vnd_id.partner_id.id
			if not partner_id:
				raise osv.except_osv('No Partner for Deposit !', "The deposit border named '%s' has no partner, please set one !" % (lots[0].bord_vnd_id.name,))

			tax_id_list = [c.id for c in lots[0].auction_id.seller_costs]
			if lots[0].bord_vnd_id.tax_id:
				tax_id_list.append(lots[0].bord_vnd_id.tax_id.id)

			acc_payable = ir.ir_get(cr, uid, [('meta','res.partner'), ('name','account.payable')], [('id',str(partner_id)), ('uid',str(uid))])[0][2]
			addresses = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact','invoice'])

			# create invoice lines
			lines = []
			for lot in lots:
				if lot.obj_price>0:
					# create invoice line for this object
					lot_name = str(lot.obj_num) + '. ' + lot.name.decode('utf8')
					if len(lot_name)>40:
						lot_name = lot_name[:37].encode('utf8') + '...'
					else:
						lot_name = lot_name.encode('utf8')

#CHECKME: c'est normal que tax_id_list soit calcule pr ts les objets et non	par objet????
					lines.append({
						'name': lot_name,
						'account_id': lot.auction_id.acc_expense, #source account
						'price_unit': lot.obj_price,
						'quantity': 1,
						'invoice_line_tax_id': tax_id_list})


			# create manual tax lines (if some objects have a net limit or some extra taxes have been entered)
#CHECKME: these 4 lines are untested !!!!!!!!!!!!!!!!!!!!!
			lot_ids = [l.id for l in lots]
			manual_costs = compute_seller_costs(cr, uid, lot_ids, True)
			acc_expense = lots[0].auction_id.acc_expense.id
			manual_tax_lines = [c.update({'manual': True, 'account_id': acc_expense}) for c in manual_costs]

			if len(lines):
				inv_id = self.pool.get('account.invoice').create(cr, uid, {
					'name': 'Auction'+': '+lots[0].auction_id.name+', '+str(len(lots))+' lot(s)',
					'type': 'in_invoice',
					'state': 'draft',
					'reference': 'Auction',	#CHECKME: c'est pas un peu court?
					'partner_ref': lot.bord_vnd_id.name, #CHECKME: c'est juste ca?
					'project_id': lot.auction_id.project_id.id,
					'partner_id': partner_id,
					'address_contact_id': addresses['contact'],
					'address_invoice_id': addresses['invoice'],
					'account_id': acc_payable,
					'invoice_line': map(lambda x:(0,0,x), lines),
					'tax_line': map(lambda x: (0,0,x), manual_tax_lines)
				})

				wf_service = netsvc.LocalService("workflow")
#Ged> proforma???? c'est normal ca?
				wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_proforma', cr)


	def lots_invoice_and_cancel_old_invoice(self, cr, uid, ids, invoice_number=False, buyer_id=False, action=False):
		lots = self.read(cr, uid, ids, ['ach_inv_id'])

		num_invoiced = 0
		inv_ids = {}
		for lot in lots:
			if lot['ach_inv_id']:
				inv_ids[lot['ach_inv_id'][0]] = True
				num_invoiced += 1

		if num_invoiced:
			if not invoice_number:
				# if some objects were already invoiced and the user didn't specify an invoice number,
				# raise an exception
				raise orm.except_orm('UserError', ('%d object(s) are already invoiced !' % (num_invoiced,), 'init'))
			else:
				wf_service = netsvc.LocalService("workflow")
				# if the user gave an invoice number, cancel the old invoices containing
				# the selected objects
				for id in inv_ids:
					wf_service.trg_validate(uid, 'account.invoice', id, 'invoice_cancel', cr)

		# create a new invoice for the selected objects
		return self.lots_invoice(cr, uid, ids, invoice_number, buyer_id, action)

	def lots_invoice(self, cr, uid, ids, invoice_number=False, buyer_id=False, action=False):
		"""
			Create an invoice for selected lots (IDS) to BUYER_ID.
			Set created invoice to the ACTION state.
			PRE:
				ACTION:
					False: no action
					xxxxx: set the invoice state to ACTION

			RETURN: id of generated invoice
		"""
		dt = time.strftime('%Y-%m-%d')

		lots = self.browse(cr, uid, ids)
		if not len(lots):
			return []

		partner_ref = lots[0].ach_login
		auction = lots[0].auction_id
		proj_id = auction.project_id.id
		auction_ref = auction.auction1
		account_id = auction.acc_income

#TODO: passer par le systeme de traduction
		auction_name = u'Veiling van ' + auction_ref + u', Kopersnr: '+(partner_ref or '')+ u', %d lot(en)' %(len(lots),)
		account_receive_id=ir.ir_get(cr,uid,[('meta','res.partner'), ('name','account.receivable')], (buyer_id or []) and [('id',str(buyer_id))] )[0][2]

		lines = []
		for lot in lots:
			price = lot.obj_price or 0.0

			lot_name = str(lot.obj_num) + '. ' + lot.name.decode('utf8')
			if len(lot_name)>40:
				lot_name = lot_name[:37].encode('utf8') + '...'
			else:
				lot_name = lot_name.encode('utf8')

#CHECKME: prob si buyer_costs est null? je pense pas qu'il puisse etre null mais bon...
			costs_ids = [c.id for c in auction.buyer_costs]
			if lot.author_right:
				costs_ids.append(lot.author_right.id)

			lines.append((0,False, {'name': lot_name, 'quantity':1, 'account_id':account_id, 'price_unit':price, 'invoice_line_tax_id': costs_ids}))

		if buyer_id:
			adrs = self.pool.get('res.partner').address_get(cr, uid, [buyer_id], ['contact','invoice'])
		else:
			adrs = {'contact':False, 'invoice':False}

		new_invoice = {
			'name': auction_name[:60],
			'reference': auction_ref,
			'project_id': proj_id,
			'state': 'draft',
			'partner_id': buyer_id,
			'address_contact_id': adrs['contact'],
			'address_invoice_id': adrs['invoice'],
			'partner_ref': partner_ref,
			'date_invoice': dt,
			'date_due': dt,
			'invoice_line': lines,
			'type': 'out_invoice',
			'account_id': account_receive_id,
		}

		if invoice_number:
			new_invoice['number'] = invoice_number

		inv_id = self.pool.get('account.invoice').create(cr, uid, new_invoice)

		if action:
			wf_service = netsvc.LocalService("workflow")
			wf_service.trg_validate(uid, 'account.invoice', inv_id, action, cr)
		self.write(cr, uid, ids, {'ach_inv_id':inv_id, 'ach_uid':buyer_id, 'state':'invoiced'})
		return inv_id

	def lots_pay(self, cr, uid, ids, buyer_id, account_id, amount):
		lots = self.browse(cr, uid, ids)
		if not len(lots):
			return True

		partner_ref = lots[0].ach_login
		auction = lots[0].auction_id
		project_id = auction.project_id.id
		auction_ref = auction.auction1
		account_src_id = ir.ir_get(cr,uid,[('meta','res.partner'), ('name','account.receivable')], (buyer_id or []) and [('id',str(buyer_id))] )[0][2]

#TODO: passer par le systeme de traduction
		auction_name = u'Auction ' + auction_ref + u', Part.: '+(partner_ref or '')+ u', %d lot(s)' %(len(lots),)

		transfer = {
			'name': auction_name[:60],
			'project_id': project_id,
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
	_columns = {
		'partner_id': fields.many2one('res.partner', 'Buyer Name', required=True),
		'contact_tel':fields.char('Contact',size=64),
		'name': fields.char('Bid ID', size=64,required=True),
		'auction_id': fields.many2one('auction.dates', 'Auction Date', required=True),
		'bid_lines': fields.one2many('auction.bid_line', 'bid_id', 'Bid'),
	}
auction_bid()

class auction_bid_lines(osv.osv):
	_name = "auction.bid_line"
	_columns = {
		'name': fields.char('Name',size=64),
		'bid_id': fields.many2one('auction.bid','Bid ID', required=True),
		'lot_id': fields.many2one('auction.lots','Lot', required=True),
		'call': fields.boolean('To be Called'),
		'price': fields.float('Maximum Price')
	}
auction_bid_lines()
