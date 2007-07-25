
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from report import report_sxw
from osv import osv

class order(report_sxw.rml_parse):
 def order_list(self, cr,uid,ids):

##        obj_cat=self.pool.get('lunch.category')
##        res=obj_cat.search(cr,uid,[])
##        res=obj_cat.browse(cr,uid,obj_cat,['cat_sequence'])
##
        moveline_obj = pooler.get_pool(self.cr.dbname).get('lunch.order')         
#        obj=self.browse(cr,uid,ids)
        cr.execute("select lo.user_id,lo.product,lo.descript,lp.price from lunch_order lo join lunch_product lp on lo.product=lp.name join lunch_category lc on lp.category_id=lc.name order by lc.category desc")
        res=cr.fetchall()

        for r in res:
            if not res:
                self.ret_list.append(0.0)
            else:
                ret_dict={
                'user_id':res[0]['user_id'],
                'product':res[0]['product'],
                'descript':res[0]['descript'],
                'price':res[0]['price']
                        }

            self.ret_list.append(ret_dict)
	return self.ret_list
		

	def __init__(self, cr, uid, name, context):
		super(order, self).__init__(cr, uid, name, context)
		user=self.pool.get('res.users').browse(cr,uid,uid)
	#	partner = user.company_id.partner_id
	#	address=partner.address and partner.address[0] or ""
	#	street = address and address.street or ""
	#	city=address and address.city
	#	tel=address and address.mobile

		self.localcontext.update({
		'time': time,
     #   'street': street,
      #  'tel':tel,
       # 'city':city,
        #'oder_list': self.order_list,
	    })
	def _add_header(self, node):
		return True

	
report_sxw.report_sxw('report.lunch.order','lunch.order','addons/lunch/report/order.rml',parser=order)
