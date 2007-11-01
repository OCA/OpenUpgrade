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

			self.cr.execute('select * from auction_buyer_taxes_rel abr,auction_dates ad where ad.id=abr.auction_id and ad.id=%d'%(ad_id[0],))
			print "Befrore fetch"
			res=self.cr.fetchall()
			print "4444444444444444444444444444444444", res
			total=0
			for r in res:
				print "rrrrrrrrrr",r[1]
				buyer_rel_field = self.pool.get('account.tax').read(self.cr,self.uid,r[1],['amount'])
				print "TAX NAMEl:********",buyer_rel_field
				total = total + buyer_rel_field['amount']

			auc_dates_fields['amount']=total
			auct_dat.append(auc_dates_fields)
			print "kkkkkkkkkkkkkkkkkkkkkkkkk",auct_dat
		print "AUC_DATTTTTTTT",auct_dat
		return auct_dat





	def lines_lots_auct_lot(self,obj):
		print "*********in LOT FUNCTION"
		auc_lot_ids = []

		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))
#
		self.cr.execute('select * from auction_lots where auction_id=%d'%(auc_date_ids[0]))
		res = self.cr.dictfetchall()

#		print "RESSSSSSSSSSSSSS",res
		rec=[]
		for r in res:
			print "OBJPRICE*******", r['obj_price']
			if not r['obj_price'] == 0:
				print "OBJPRICEnot >0*******", r['obj_price']
				rec.append(r)

		for r in rec:
			if r['ach_uid']:
				tnm=self.pool.get('res.partner').read(self.cr,self.uid,[r['ach_uid']],['name'])
#				print "tnm::::::::",tnm
				r.__setitem__('ach_uid',tnm[0]['name'])
				print "BUYERNAMEACH_UID",r['ach_uid']
#			print "BUYERNAMEACH_UID if NOT BUYER******",r['ach_uid']
		return rec



	def sum_adj_price(self,obj):
#		print "*********in LOT FUNCTION"
		auc_lot_ids = []
#
		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))

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

		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))

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
		return sum


	def sum_buyer_price(self,obj):
#		print "*********in LOT FUNCTION"
		auc_lot_ids = []
		auc_date_ids = self.pool.get('auction.dates').search(self.cr,self.uid,([('name','like',obj['name'])]))
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

		return sum

report_sxw.report_sxw('report.buyer.list', 'auction.lots', 'addons/auction/report/buyer_list.rml', parser=buyer_list)