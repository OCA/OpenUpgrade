##############################################################################
#
# Copyright (c) 2005 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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


import pooler
import time
from report import report_sxw
from osv import osv

class buyer_list(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(buyer_list, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
#			'sum_taxes': self.sum_taxes,
#			'sum_debit_buyer': self.sum_debit_buyer,
			'lines_lots_from_auction' : self.lines_lots_from_auction,
			'lines_lots_auct_lot' : self.lines_lots_auct_lot,
			'sum_adj_price':self.sum_adj_price,
			'sum_buyer_obj_price':self.sum_buyer_obj_price,
			'sum_buyer_price':self.sum_buyer_price


	})



	def lines_lots_from_auction(self,objects):
#		print "*********in the function"


		auc_lot_ids = []
#		print "OBJECTSS*********",objects
		for lot_id  in objects:
#			print "LOTID",lot_id
			auc_lot_ids.append(lot_id.id)
#		print "selected lots: ",auc_lot_ids
		self.cr.execute('select auction_id from auction_lots where id in ('+','.join(map(str,auc_lot_ids))+') group by auction_id')
		auc_date_ids = self.cr.fetchall()
#		print "AUCTION DATE IDS***************",auc_date_ids
		auct_dat=[]
		for ad_id in auc_date_ids:
			print "s***********",ad_id[0]
			auc_dates_fields = self.pool.get('auction.dates').read(self.cr,self.uid,ad_id[0],['name'])

			print "AUCTION DATE FIELDS",auc_dates_fields
##			############new cdding for the buyer cost
#			self.cr.execute('select abr.auction_id,abr.tax_id  from auction_buyer_taxes_rel abr,auction_dates ad where ad.id=abr.auction_id and ad.id=1;
#			auc_buyer_rel_ids = self.pool.get('auction.buyer.taxes.rel').search(self.cr,self.uid,([('auction_id','=',auc_dates_fields['id'])]))

#			print "VIRTULA TABLE IDS",auc_buyer_rel_ids

			auct_dat.append(auc_dates_fields)

		print "AUCT LIST",auct_dat
#		print "LIST ******FIELDS",auct_dat[0]['name']

#		sql='#		 select id,name from auction_lots where auction_id in (select id from auction_dates where name = 'painting Exhibition');'
#		print "RETURN************"
		return auct_dat


#	def lines_lots_auct_lot(self,obj):
#		print "*********in LOT FUNCTION"
#		auc_lot_ids = []
#		print "OBJECTSS*********",objects
#		for lot_id  in objects:
#			print "LOTID",lot_id
#			auc_lot_ids.append(lot_id.id)
#		print "selected lots: ",auc_lot_ids
#		self.cr.execute('select auction_id from auction_lots where id in ('+','.join(map(str,auc_lot_ids))+') group by auction_id')
#		auc_date_ids = self.cr.fetchall()
#		print "AUCTION DATE IDS***************",auc_date_ids
#
#		auct_dat=[]
#		for ad_id in auc_date_ids:
#			print "s***********",ad_id[0]
#			auc_lots_ids = self.pool.get('auction.lots').search(self.cr,self.uid,([('auction_id','=',ad_id[0])]))
#			print "*********auction_lot id",auc_lots_ids
#			auc_lot_obj=self.pool.get('auction.lots').browse(self.cr,self.uid,auc_lots_ids)
#			print "********AUCTION_LOT _OBJECT",auc_lot_obj[0].name
#			for id in auc_lot_obj:
#				print "IDSSSSSSSSSSS",id
#				auct_dat.append(id)


	def lines_lots_auct_lot(self,obj):
		print "*********in LOT FUNCTION"
		auc_lot_ids = []
#		print "OBJECTSS*********",obj
#		for lot_id  in objects:
#			print "LOTID",lot_id
#			auc_lot_ids.append(lot_id.id)
#		print "name colum ",obj['name']
		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))
#		print "AUCTION DATE IDS",auc_date_ids

		#self.cr.execute('select * from auction_lots where auction_id +auc_date_idsgroup by auction_id')
#		print 'select * from auction_lots where auction_id=%d'%(auc_date_ids[0])
		self.cr.execute('select * from auction_lots where auction_id=%d'%(auc_date_ids[0]))
		res = self.cr.dictfetchall()

#		print "RESSSSSSSSSSSSSS",res
		rec=[]
		for r in res:
			print "OBJPRICE*******", r['obj_price']
			if not r['obj_price'] == 0:
				print "OBJPRICEnot >0*******", r['obj_price']
				rec.append(r)
#				print "OBJ_PRICENOT  >0",r['obj_price']
#			print "rrrrrrrrrrr////////",r,r['ach_uid']
		for r in rec:
			if r['ach_uid']:
				tnm=self.pool.get('res.partner').read(self.cr,self.uid,[r['ach_uid']],['name'])
#				print "tnm::::::::",tnm
				r.__setitem__('ach_uid',tnm[0]['name'])

#
		return rec



	def sum_adj_price(self,obj):
#		print "*********in LOT FUNCTION"
		auc_lot_ids = []
#		print "OBJECTSS*********",obj
#		for lot_id  in objects:
#			print "LOTID",lot_id
#			auc_lot_ids.append(lot_id.id)
#		print "name colum ",obj['name']
		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))
#		print "AUCTION DATE IDS",auc_date_ids

		#self.cr.execute('select * from auction_lots where auction_id +auc_date_idsgroup by auction_id')
#		print 'select * from auction_lots where auction_id=%d'%(auc_date_ids[0])
		self.cr.execute('select * from auction_lots where auction_id=%d'%(auc_date_ids[0]))
		res = self.cr.dictfetchall()
#		print "RESSSSSSSSSSSSSS",res
		sum=0
		rec=[]
		for r in res:
			print "OBJPRICE*******", r['obj_price']
			if not r['obj_price'] == 0:
				print "OBJPRICEnot >0*******", r['obj_price']
				rec.append(r)
		for r in rec:
			sum = sum + r['obj_price']
#		print "VALUE OF OBJ_SUM",sum
		return sum

	def sum_buyer_obj_price(self,obj):
#		print "*********in LOT FUNCTION"
		auc_lot_ids = []
#		print "OBJECTSS*********",obj
#		for lot_id  in objects:
#			print "LOTID",lot_id
#			auc_lot_ids.append(lot_id.id)
#		print "name colum ",obj['name']
		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))
#		print "AUCTION DATE IDS",auc_date_ids

		#self.cr.execute('select * from auction_lots where auction_id +auc_date_idsgroup by auction_id')
#		print 'select * from auction_lots where auction_id=%d'%(auc_date_ids[0])
		self.cr.execute('select * from auction_lots where auction_id=%d'%(auc_date_ids[0]))
		res = self.cr.dictfetchall()
#		print "RESSSSSSSSSSSSSS",res
		rec=[]
		sum=0
		for r in res:
			if not r['obj_price'] == 0:
				print "OBJPRICEnot >0*******", r['obj_price']
				rec.append(r)
		for r in rec:
			sum=sum + r['buyer_price']-r['obj_price']

#		print "SUM OF BUYER PRICE -OBJPRICE",sum
		return sum


	def sum_buyer_price(self,obj):
#		print "*********in LOT FUNCTION"
		auc_lot_ids = []
#		print "OBJECTSS*********",obj
#		for lot_id  in objects:
#			print "LOTID",lot_id
#			auc_lot_ids.append(lot_id.id)
#		print "name colum ",obj['name']
		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))
#		print "AUCTION DATE IDS",auc_date_ids

		#self.cr.execute('select * from auction_lots where auction_id +auc_date_idsgroup by auction_id')
#		print 'select * from auction_lots where auction_id=%d'%(auc_date_ids[0])
		self.cr.execute('select * from auction_lots where auction_id=%d'%(auc_date_ids[0]))
		res = self.cr.dictfetchall()
#		print "RESSSSSSSSSSSSSS",res
		sum=0
		rec=[]
		for r in res:
			if not r['obj_price'] == 0:
				print "OBJPRICEnot >0*******", r['obj_price']
				rec.append(r)
		print "REC***************",rec
		for r in rec:
			print "buyerprice********", r['buyer_price']
			sum = sum + r['buyer_price']
		print "SUM OF BUYER PRICE -OBJPRICE",sum
#
		return sum




#	def sum_taxes(self, lot):
##		buyer_cost = self.pool.get('auction.dates').read(self.cr,self.uid,[auction_id],['buyer_costs'])[0]
##		total_amount = 0.0
##		for id in buyer_cost['buyer_costs'] :
##			amount = self.pool.get('account.tax').read(self.cr,self.uid,[id],['amount'])[0]['amount']
##			total_amount += (amount*obj_price)
##		 return total_amount
#		amount=0.0
#		taxes=[]
#		taxes = lot.product_id.taxes_id
#		taxes += lot.auction_id.buyer_costs
#		if lot.author_right:
#			taxes+=lot.author_right
#		tax=self.pool.get('account.tax').compute(self.cr,self.uid,taxes,lot.obj_price,1)
#		for t in tax:
#			amount+=t['amount']
#		print "amount",amount
#		print "tax",tax
#		return amount
#
#	def sum_debit_buyer(self,auc_id):
#		#auct_id=object.auction_id.id
##		 select id,name from auction_lots where auction_id in (select id from auction_dates where name = 'painting Exhibition');
#
#		self.cr.execute('select buyer_price,is_ok,obj_price,ach_uid, from auction_lots where auction_id=%d'%(auct_id,))
#		res = self.cr.fetchone()
#		print "***************VALUES OF RES",res[0]
#		return str(res[0] or 0)


report_sxw.report_sxw('report.buyer.list', 'auction.lots', 'addons/auction/report/buyer_list.rml', parser=buyer_list)