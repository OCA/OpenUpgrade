##############################################################################
#
# Copyright (c) 2005-2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
import reportlab
import reportlab.lib.units
import urllib
import base64
from report import report_sxw

class product_catalog(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(product_catalog, self).__init__(cr, uid, name, context)

        self.localcontext.update({
            'time': time,
            'image_url' : self._get_imagepath,
            'currency_code': self._get_currency,
#            'Carton': self._get_carton,
#            'SCondt': self._get_SCondt,
#            'UV': self._get_UV,
            'categories':self._getCategories,
            'products':self._getProducts,
            'description':self._get_desc,
            'packaging_title':self._get_packaging_title,
            'packaging_value':self._get_packaging_value,
            'Price':self._get_price,

        })
    def _get_imagepath(self,product):
        attach_ids = self.pool.get('ir.attachment').search(self.cr, self.uid, [('res_model','=','product.product'), ('res_id', '=',product)])
        datas = self.pool.get('ir.attachment').read(self.cr, self.uid, attach_ids)
        if len(datas):
            # if there are several, pick first
            try:
                if datas[0]['link']:
                    try:
                        img_data =  base64.encodestring(urllib.urlopen(datas[0]['link']).read())
                        return img_data
                    except Exception,innerEx:
                        print innerEx
                elif datas[0]['datas']:
                    return datas[0]['datas']
            except Exception,e:
                print e
        return None

    def setCat(self,cats):
        lst = []
        for cat in cats:
            if cat not in lst:
                lst.append(cat)
                category = self.pool.get('product.category').read(self.cr,self.uid,[cat])
                if category[0]['child_id']:
                    lst.extend(self.setCat(category[0]['child_id']))
        return lst


    def _getCategories(self,cat):
        lst =  self.setCat(cat[0][2])
        cat_ids = self.pool.get('product.category').search(self.cr,self.uid,[('id','in',lst)])
        tmpCat_ids = []
        for cat in cat_ids:
            prod_ids = self.pool.get('product.template').search(self.cr,self.uid,[('categ_id','=',cat)])
            if len(prod_ids):
                tmpCat_ids.append(cat)
        cats = self.pool.get('product.category').read(self.cr,self.uid,tmpCat_ids)
        return cats
    def _getProducts(self,category,lang):
        prod_tmpIDs = self.pool.get('product.template').search(self.cr,self.uid,[('categ_id','=',category)])
        prod_ids = self.pool.get('product.product').search(self.cr,self.uid,[('product_tmpl_id','in',prod_tmpIDs)])
        prods = self.pool.get('product.product').read(self.cr,self.uid,prod_ids,context={'lang':lang})
        return prods

    def _get_currency(self):
        return self.pool.get('res.users').browse(self.cr, self.uid, [self.uid])[0].company_id.currency_id.name


    def _get_packaging_title(self,product,index):
        packaging_ids = self.pool.get('product.packaging').search(self.cr,self.uid,[('product_id','=',product)],limit=4)
        packs = self.pool.get('product.packaging').read(self.cr,self.uid,packaging_ids)
        if len(packs) > index:
            s = str(packs[index]['name'])
            if len(s)>9:
                p = str(s[0:9]) + "..."
                return p
            elif not s == "False":
                return s
        return " "

    def _get_packaging_value(self,product,index):
        packaging_ids = self.pool.get('product.packaging').search(self.cr,self.uid,[('product_id','=',product)],limit=4)
        packs = self.pool.get('product.packaging').read(self.cr,self.uid,packaging_ids)
        if len(packs) > index:
            return str(packs[index]['qty'])
        return False

    def _get_price(self,product,pricelist):
        price = self.pool.get('product.pricelist').price_get(self.cr,self.uid,[pricelist], product, 1.0, None,{'uom': False})[pricelist]
        if not price:
            price = 0.0
        return price

    def _get_desc(self,tempate_id):
        if tempate_id:
            prodtmpl = self.pool.get('product.template').read(self.cr,self.uid,[tempate_id])[0]

            if prodtmpl['description_sale']:
                return prodtmpl['description_sale']
            else:
                return "no Description Specified"
        else:
            return "This is Test Description"


report_sxw.report_sxw('report.product_catalog', 'res.partner', 'addons/product_catalog_report/report/product_catalog.rml', parser=product_catalog,header=False)


