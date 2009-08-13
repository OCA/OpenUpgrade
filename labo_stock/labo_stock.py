# -*- encoding: utf-8 -*-
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


import ir
from mx import DateTime

import datetime
from osv import fields,osv,orm
import pooler
import netsvc
import time
from xml.dom import minidom


class mix_category(osv.osv):
	_name = 'mix.category'
	_columns = {
		'active': fields.boolean('Active'),
		'name': fields.char('Name', size=64, required=True, select=True),
	}
mix_category()

class amorces_category(osv.osv):
	_name = 'amorces.category'
	_columns = {
		'name': fields.char('Name', size=64, required=True, select=True),
		'pref': fields.char('Prefix', size=64, select=True),
	}
amorces_category()

#class labo_article_category(osv.osv):
#	_name = 'labo.article.category'
#	_columns = {
#		'name': fields.char('Name', size=64, required=True, select=True),
#		'active' : fields.boolean('Active'),
#	}
#	_defaults = {
#		'active' : lambda *a: 1,
#}
#labo_article_category()
class labo_amorces(osv.osv):
	_name = 'labo.amorces'
	_columns = {
		'name': fields.char('Internal Number', size=64, select=True),
#		'type_id':fields.many2one('amorces.category', 'Prefix Amorce'),
		'sequence_id':fields.text('Sequence'),
		'firm_id':fields.many2one('res.partner','Firm', select=1),
		'num_lot':fields.char('Lot num', size=64),
		'rec_date': fields.date('Reception date'),
		'exp_date': fields.date('Expiration date'),
		'open_date': fields.date('Opening date'),
		'close_date': fields.date('Closing date'),
		'concentration':fields.float('Concentration'),
		'accredit':fields.boolean('Accredit'),

#		'amorce_id':fields.many2one('stock.reactives','Reactive')
	}
	def _constraint_num_upto_zero(self, cr, uid, ids):
		for amorces in self.browse(cr,uid,ids):
			if amorces.concentration and int(amorces.concentration) > 0: pass
			else: return False
		return True
#
#
#		obj_amorces = self.browse(cr, uid, ids)
#		print obj_amorces
#		c=[]
#		for a in obj_amorces:
#			print a.concentration
#			c.append(a.concentration)
#
#		for i in c:
#			if i>0:
#				return True
#			else: return False

#	_constraints = [
#		(_constraint_num_upto_zero, "Concentration should be > zero!", []),
#		]
	defaults = {
		'concentration': lambda *a: 1
}
labo_amorces()
class product_category(osv.osv):
	_inherit='product.category'
	_columns={
		'code_p':fields.char('Code', size=64)
}
product_category()

class labo_article(osv.osv):
#	_name = 'labo.article'
#	_description = "Article"
#	_table = "labo_article"
	_inherit = 'product.product'
	_columns = {

		'date_entry': fields.date('Date Entry'),
		'accredit':fields.char('Accredit', size=64),
		'store_loc':fields.many2one('stock.location','Stored In', select="1"),
		'part_n':fields.char('Part N°',size=64),
	#	'family': fields.selection([('mobility','Mobility'),('analysis','Analysis'),('materielbureau','Materiel bureau'),('disposable','Disposable'),('reactive','Reactive'),('mainoeuvre','Main-doeuvre'),('materielprelev','Material prelev'),('materiellabo','Material Lab'),('finances','Finances'),('appareillage','Appareillage'),('divers','Divers'),('kit','Kit'),('material','Materiel'),('service','Service'),('prelevement','Prélèvement'),('maintenance','Maintenance')], 'Family', select=True),
		'family': fields.selection([
								('analyses','Analyses'),
								('appareillage','Appareillage'),
								('disposable','Disposable'),
								('kit','Kit'),
								('maintenance','Maintenance'),
								('material','Matériel'),
								('prelevement','Prélèvement'),
								('reactif','Réactif'),
								('service','Service'),
								('divers','Divers')],
								'Family', select=True),
		'product_nl': fields.char('Short Description' ,size=64),
		'icar':fields.boolean('Icar'),
		'belac':fields.boolean('Belac'),
	}


	def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
		sample_id = context.get('islaboarticleprod', False)
		if sample_id:
			viewcalled = 'labo_stock_article_view_'+view_type
			view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=',viewcalled)])
			if len(view_ids):
				view_id = view_ids[0]
				return super(labo_article, self).fields_view_get( cr, user, view_id , view_type, context, toolbar)
		return super(labo_article, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)


	def onchange_pricelist(self, cr, uid, ids,supplier,context={}):
		print "IN THE ONCHANCE PRICELIST FUNCTION"
		if not supplier:
			return {'value': {'pricelist_id':False}}
		part = self.pool.get('res.partner').browse(cr, uid, supplier)
		v_part=part.property_account_receivable.id or False
		return {'value': {'pricelist_id': v_part}}


	def invoice_create(self,cr, uid,ids,context):
		print "INVOICE CREATE"
		invoices = {}
		taxes=[]
		inv_ref=self.pool.get('account.invoice')
		for article in self.browse(cr,uid,ids,context):
			partner_id = article.supplier.id
	#		req_name = req.name
			if not article.supplier.id:
				raise osv.except_osv('Missed Client !', 'The article "%s" has no client assigned.' % (article.name,))
			if (article.supplier.id) in invoices:
				inv_id = invoices[(article.supplier.id)]
			else:
				res = self.pool.get('res.partner').address_get(cr, uid, [article.supplier.id], ['contact', 'invoice'])
				contact_addr_id = res['contact']
				invoice_addr_id = res['invoice']
				inv = {
					'name': 'Article:'+ article.name,
					'partner_id':article.supplier.id ,
					'type': 'in_invoice',
				}
				inv.update(inv_ref.onchange_partner_id(cr,uid, [], 'in_invoice',article.supplier.id)['value'])
				inv_id = inv_ref.create(cr, uid, inv, context)
				invoices[article.supplier.id] = inv_id
			self.write(cr,uid,[article.id],{'invoice_ids':inv_id})
		#	if req.type_id and req.type_id.product_id:
#			taxes = map(lambda x: x.id, article.tva)
			if article.tva:
				taxes.append(article.tva.id)
				#							article.supplier.property_product_price.version_id[0].items_id.product_id.id,
		#	print "ARTICLE", article.supplier.property_product_price #.version_id[0].items_id.product_id.id, 1.0, article.supplier)[article.discount.id]
			price = article.price_cat
#			price = self.pool.get('product.pricelist').price_get(cr, uid, [article.discount.id],
#											article.id,
#											1.0, article.supplier)[article.discount.id]
			print "PRICE",price
			if price is False:
				raise osv.except_osv('No valid pricelist line found !',
				"You have to change either the product defined on the type of analysis or the pricelist.")
			inv_line= {
				'invoice_id': inv_id,
				'account_id':article.supplier.property_account_receivable.id,
				'quantity': article.qte,
		#		'product_id': article.supplier.property_product_price.version_id.items_id.product_id.id,
				'product_id': article.discount.version_id[0].items_id[0].product_id.id,
				'name': article.name,
				'invoice_line_tax_id': [(6,0,taxes)],
				'price_unit': price,
			}
			print inv_line['price_unit']
			self.pool.get('account.invoice.line').create(cr, uid, inv_line,context)
			inv_ref.button_compute(cr, uid, invoices.values())
		for inv in inv_ref.browse(cr, uid, invoices.values(), context):
			inv_ref.write(cr, uid, [inv.id], {
				'check_total': inv.amount_total
			})
			wf_service = netsvc.LocalService('workflow')
			wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_open', cr)
		return invoices.values()
#	def price_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
#		currency_obj = self.pool.get('res.currency')
#		product_obj = self.pool.get('product.product')
#		supplierinfo_obj = self.pool.get('product.supplierinfo')
#		price_type_obj = self.pool.get('product.price.type')
#
#		if context and ('partner_id' in context):
#			partner = context['partner_id']
#		date = time.strftime('%Y-%m-%d')
#		if context and ('date' in context):
#			date = context['date']
#		result = {}
#		for id in ids:
#			cr.execute('SELECT * ' \
#					'FROM product_pricelist_version ' \
#					'WHERE pricelist_id = %d AND active=True ' \
#						'AND (date_start IS NULL OR date_start <= %s) ' \
#						'AND (date_end IS NULL OR date_end >= %s) ' \
#					'ORDER BY id LIMIT 1', (id, date, date))
#			plversion = cr.dictfetchone()
#
#			if not plversion:
#				raise osv.except_osv('Warning !',
#						'No active version for the selected pricelist !\n' \
#								'Please create or activate one.')
#
#			cr.execute(
#				'SELECT i.*, pl.currency_id '
#				'FROM product_pricelist_item AS i, '
#					'product_pricelist_version AS v, product_pricelist AS pl '
#				'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %d) '
#					'AND (product_id IS NULL OR product_id = %d) '
#					'AND (' + categ_where + ' OR (categ_id IS NULL)) '
#					'AND price_version_id = %d '
#					'AND (min_quantity IS NULL OR min_quantity <= %f) '
#					'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
#				'ORDER BY sequence LIMIT 1',
#				(tmpl_id, prod_id, plversion['id'], qty))

#	_defaults = {
#		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'labo.article'),
#}
labo_article()



class labo_type_reactives(osv.osv):
	_name='labo.type.reactives'
	_rec_name='code'
	_columns={
	'desc': fields.char('Description',size=256, select=True),
	'code': fields.char('Code',size=64, select=True),
	}
labo_type_reactives()

class stock_reactives(osv.osv):
	_name = 'stock.reactives'
	_columns = {
		'product_id':fields.many2one('product.product','Article', select=1),
		'family': fields.selection([('search_react','Searches'),('analysis','Analysis')], 'Type of reactives',select=True),
		'rec_date': fields.date('Reception date'),
		'exp_date': fields.date('Expiration date'),
		'exp_date2': fields.date('Expiration date 2'),
		'open_date': fields.date('Opening date'),
		'close_date': fields.date('Closing date'),
#		'reactive_id':fields.many2many('labo.amorces','amorce_react_rel','amorce_id','react_id','Amorces'),
#		'name':fields.char('Internal number', size=6, required=True),
		'internal_num':fields.char('Lot number', size=60, select=1),
		'name':fields.char('Internal number', size=10, select=1),
		'categ_id':fields.many2one('labo.type.reactives','Type', select=1),
#		'locality_storing':fields.char('Stored in', size=64, select=1),
#		'sale_o':fields.many2one('sale.order', 'Sale order'),
		'send_date': fields.date('Sending date'),
		'testing_date': fields.date('Testing validation'),

		'history_id':fields.one2many('reactive.history','reactive_id','History',readonly=True)
	}
	_defaults = {
#		'storing_loc':fields.many2one('stock.location', 'Stored in', select=1),
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'stock.reactives'),
		'rec_date': lambda *a: time.strftime('%Y-%m-%d'),
#		'accredit':lambda *a: 'O',
}
stock_reactives()


class reactive_history(osv.osv):
	_name = "reactive.history"
	_description="Reactive history"
	_columns = {
		'name': fields.date('Date',size=64),
		'reactive_id': fields.many2one('stock.reactives','Reactives'),
}
reactive_history()

class form_mix(osv.osv):
	_name='form.mix'

	def calc_water_rate(self, cr, uid, ids, *a):
		res={}
		for i in self.browse(cr, uid, ids):
			try:
				total=0.0
				for mix in i.mix_id:
				#	if (mix.amorce_id.concentration==0):
				#		raise osv.except_osv('Amorce concentration  !', 'The amorce  "%s" has zero in it s concentration.' % (mix.amorce_id.id,))
				#	else:
					total += (mix.final_vol*mix.fich_id.react_nbr*mix.vol_mix)/(mix.amorce_id.concentration)
				res[i.id] = (i.react_nbr*i.vol) - total
			except:
				res[i.id] = 0.0
		return res


	_columns={
		'compos_name':fields.char('Number',size=64),
		'categ_id':fields.many2one('mix.category','Prefix'),
		'date_fich': fields.date('Date', select=1),
		'comp_nbr': fields.integer('Composition number'),
		'react_nbr': fields.integer('Reactions number'),
		'name':fields.char('Composition Name',size=64, required= True, select=1),
		'user_id':fields.many2one('res.users','Responsible', select=1),
		'vol':fields.float('Volume by reactions'),
		'mix_id':fields.one2many('labo.mix', 'fich_id','Mix'),
		'water_rate':fields.function(calc_water_rate,method=True,string='H2O')
	}
	_defaults = {
		'date_fich': lambda *a: time.strftime('%Y-%m-%d'),
}
form_mix()

class labo_mix(osv.osv):
	_name='labo.mix'
	_rec_name='vol_mix'

	def volume_to_take(self, cr, uid, ids, *a):
		calc_take=0
		res = {}
	#	mixes=self.pool.get('form.mix').browse(cr,uid,ids)
		for mix in self.browse(cr, uid, ids):
			try:
				if mix.amorce_id.concentration:
					res[mix.id] = (mix.final_vol*mix.fich_id.react_nbr*mix.vol_mix)/(mix.amorce_id.concentration)
				else:
					res[mix.id]= mix.final_vol*mix.fich_id.react_nbr*mix.vol_mix
			except:
				res[mix.id] = 0.0
		return res

	_columns={
#		'name':fields.char('Amorce',size=64, select=1),
		'vol_mix':fields.float('Concentration(µM)'),
		'final_vol':fields.float('Final concentration'),
		'amorce_num':fields.char('Lot', size=64),
	#	'vol_take':fields.float('Volume to take'),
		'amorce_id':fields.many2one('labo.amorces', 'Amorce', select=1),
		'fich_id':fields.many2one('form.mix','Form'),
		'vol_take':fields.function(volume_to_take,string='Volume to take', method=True),
	}


	def onchange_volume(self, cr, uid, ids,amorce_id,context={}):
		if not amorce_id:
			return {'value': {'vol':False}}
		mix = self.pool.get('labo.amorces').browse(cr, uid, amorce_id)
		v_mix=mix.concentration or 0
		num=mix.name or ""
		print ids
		try:
			v_take = self.volume_to_take(cr, uid, ids)[ids[0]]
			return {'value': {'vol_mix': v_mix,'amorce_num':num,'vol_take':v_take}}
		except:
			return {'value': {'vol_mix': v_mix,'amorce_num':num}}

labo_mix()

#class product_pricelist_item(osv.osv):
#	_inherit = "product.pricelist.item"
#	_columns = {
#			    'article_id':fields.many2one('labo.article', 'Article'),
#			    }
#	def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
#		res = super(product_pricelist_item,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
#		print "Context :",context
#		arch = res['arch']
#		arch_dom = minidom.parseString(arch)
#		remove_list = [x for x in arch_dom.firstChild.childNodes if x.nodeType == x.ELEMENT_NODE and x.getAttribute('name') in ['product_id','product_tmpl_id','categ_id']]
#		new_node = remove_list[1].cloneNode(0)
#		new_node.setAttribute('name','article_id')
#		print "new Node:",new_node
#		arch_dom.firstChild.insertBefore(new_node,remove_list[0])
#		for rm_node in remove_list:
#			arch_dom.firstChild.removeChild(rm_node)
#		print "arch_dom :",arch_dom.toxml()
#		res['arch'] = arch_dom.toxml()
#		res['fields'].update({'article_id':{'string':'Article','type':'many2one','relation':'labo.article'}})
#		return res
#product_pricelist_item()

#class product_pricelist(osv.osv):
#	_inherit = "product.pricelist"
#	def price_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
#
