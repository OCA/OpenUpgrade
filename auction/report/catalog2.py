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

import datetime
import time
from report.interface import report_rml
from report.interface import toxml
import pooler
from osv import osv
from time import strptime

from xml.dom import minidom

import sys
import os
import re
import netsvc

def escape(s):
    return str(s or '').replace('<br/>','').decode('latin1','replace').encode('utf-8')

class auction_catalog(report_rml):

    def create_xml(self, cr, uid, ids, data, context):
        xml = self.catalog_xml(cr, uid, ids, data, context)
        return self.post_process_xml_data(cr, uid, xml, context)

    def catalog_xml(self,cr,uid,ids,data,context):
        impl = minidom.getDOMImplementation()
        doc = impl.createDocument(None, "report", None)
        infodb='info'
        commdb='comm'
        tab_avoid = []
        tab_no_photo=[]

        sql = 'select name as info,auction1,expo1,auction2,expo2 from auction_dates where id = 1'
        cr.execute(sql)
#        res = cr.fetchone()
        res = cr.dictfetchone()
        print "Main Auction Resource:",res
        key = 'info'
        categ = doc.createElement(key)
        categ.appendChild(doc.createTextNode(escape(res["info"])))
        doc.documentElement.appendChild(categ)

#        expo_date = "%d-%d-%d" % (res['expo1'].day, res['expo1'].day, res['expo1'].day)
#        print "expo Date: ", expo_date
#        if (res['expo2']):
#            expo_date += " / %d-%d-%d" % (res["expo2"].day, res["expo2"].month, res["expo2"].year)
#        auction_date = "%d-%d-%d" % (res["auction1"].day, res["auction1"].month, res["auction1"].year)
#        if (res['auction2']):
#            auction_date += " / %d-%d-%d" % (res["auction2"].day, res["auction2"].month, res["auction2"].year)

        categ = doc.createElement("auction-date")
        categ.appendChild(doc.createTextNode(escape('2007-08-05')))
        doc.documentElement.appendChild(categ)
        categ = doc.createElement("expo-date")
        categ.appendChild(doc.createTextNode(escape('2007-08-05')))
        doc.documentElement.appendChild(categ)

#        no_highlight = tab_avoid+tab_no_photo
#        if len(no_highlight)>1:
#            where_no_high = " and ref not in "+str(tuple(no_highlight))
#        elif len(no_highlight)==1:
#            where_no_high = " and ref!='%s' " % str(no_highlight[0])
#        else :
#            where_no_high = ''

        cr.execute('select distinct(image) from auction_lots where image is not null and auction_id = 1')
        res = cr.dictfetchall()

        for i in range(len(res)):
            promo = doc.createElement('promotions'+str(i+1))
            promo.appendChild(doc.createTextNode('/home/pmo/Desktop/auction_belgium4.1.1/auction_project/bin/images/crm.jpg'))
            doc.documentElement.appendChild(promo)


        products = doc.createElement('products')
        doc.documentElement.appendChild(products)

        side = 0
        length = 0

        cr.execute('select * from auction_lots where auction_id = 1')
        res = cr.dictfetchall()

        print res
        for cat in res:
            product =doc.createElement('product')
            products.appendChild(product)

#            for key in ('ref','artist'):
#                ref1 = doc.createElement(key)
#                ref1.appendChild(doc.createTextNode( escape(cat[key])))
#                product.appendChild(ref1)

            if cat['name']:
                infos = doc.createElement('infos')
                lines = re.split('<br/>|\n', cat['name'])
    #            lines = cat['info'].splitlines()
                for line in lines:
                    xline = doc.createElement('info')
                    xline.appendChild(doc.createTextNode(escape(line)))
                    infos.appendChild(xline)
                product.appendChild(infos)

            for key in ('lot_est1','lot_est2'):
                ref2 = doc.createElement(key)
                ref2.appendChild(doc.createTextNode( escape(cat[key] or 0.0)))
                product.appendChild(ref2)

            oldlength = length
            length += 2.0

#            if cat['image'] :
#                dest = os.path.join('/home/pmo/Desktop/auction_belgium4.1.1/auction_project/bin/images/crm.jpg')
#                ref = doc.createElement('photo')
#
##                if cat['ref'] not in dict_size.keys():
##                    ref = doc.createElement('photo')
##                    size = photo_shadow.convert_catalog('/home/pmo/Desktop/auction_belgium4.1.1/auction_project/bin/images/crm.jpg', dest)
##                elif dict_size[cat['ref']]=='S':
##                    ref = doc.createElement('photo_small')
##                    size = photo_shadow.convert_catalog('/home/pmo/Desktop/auction_belgium4.1.1/auction_project/bin/images/crm.jpg', dest, 110)
##                else :
##                    ref = doc.createElement('photo_large')
##                    size = photo_shadow.convert_catalog('/home/pmo/Desktop/auction_belgium4.1.1/auction_project/bin/images/crm.jpg', dest, 440)
#                ref.appendChild(doc.createTextNode(dest))
#                product.appendChild(ref)
##                if size[1]>=size[0]:
##                    length += 4.5
##                else:
##                    length += (4.5 * size[1])/size[0]
#
#            else:
#                length += 2.0

            if length>23.7:
                side += 1
                length = length - oldlength
                ref3 = doc.createElement('newpage')
                ref3.appendChild(doc.createTextNode( "1" ))
                product.appendChild(ref3)

            if side%2:
                ref4 = doc.createElement('side')
                ref4.appendChild(doc.createTextNode( "1" ))
                product.appendChild(ref4)

        xml1 = doc.toxml()
        print "generated : \n", xml1

        xml = '<?xml version="1.0" encoding="UTF-8" ?> \n \t <report> \n',xml1,'</report>'

#        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
#        <report>
#        %s
#        </report>
#        ''' % '\n'.join(xml1)

        print "Modified xml \n", xml

        return xml

auction_catalog('report.auction.cat_flagy', 'auction.lots','','addons/auction/report/catalog2.xsl')
#
#
#    def create_xml(self, cr, uid, ids, data, context):
#        pool = pooler.get_pool(cr.dbname)
#	impl = minidom.getDOMImplementation()
#	doc = impl.createDocument(None, "catalog", None)
#
#
#	if lang=='ned':
#		infodb='info_ned'
#		commdb='comm_ned'
#
#	elif lang=='fr':
#		infodb='info_fr'
#		commdb='comm_fr'
#	else :
#		infodb='info'
#		commdb='comm'
##	print 'select '+infodb+' as info,'+commdb+' as comm,au1 as auction1,expo1,au2 as auction2, expo2 from aie_dates where '+where_did
#	cr.execute('select '+name+' as info,'+auction1+' as auction1,expo1,'+auction2+' as auction2, expo2 from auction_dates where '+where_did)
#	res = cr.fetchone()
##	print res
#
#	for key in ('info'):
#		categ = doc.createElement(key)
#		categ.appendChild(doc.createTextNode(escape(res[key])))
#		doc.documentElement.appendChild(categ)
#
#	expo_date = "%d-%d-%d" % (res["expo1"].day, res["expo1"].month, res["expo1"].year)
#	if (res['expo2']):
#		expo_date += " / %d-%d-%d" % (res["expo2"].day, res["expo2"].month, res["expo2"].year)
#	auction_date = "%d-%d-%d" % (res["auction1"].day, res["auction1"].month, res["auction1"].year)
#	if (res['auction2']):
#		auction_date += " / %d-%d-%d" % (res["auction2"].day, res["auction2"].month, res["auction2"].year)
#	categ = doc.createElement("auction-date")
#	categ.appendChild(doc.createTextNode(escape(auction_date)))
#	doc.documentElement.appendChild(categ)
#	categ = doc.createElement("expo-date")
#	categ.appendChild(doc.createTextNode(escape(expo_date)))
#	doc.documentElement.appendChild(categ)
#
#	no_highlight = tab_avoid+tab_no_photo
#	if len(no_highlight)>1:
#		where_no_high = " and ref not in "+str(tuple(no_highlight))
#	elif len(no_highlight)==1:
#		where_no_high = " and ref!='%s' " % str(no_highlight[0])
#	else :
#		where_no_high = ''
#
#	cr.execute("select distinct(image) from auction_lots where image is not null and "+where_did+" and lang=%s "+where_no_high+" order by est1 desc limit 4", (lang, ))
#	res = cr.fetchall()
#
#	for i in range(len(res)):
#		promo = doc.createElement('promotions'+str(i+1))
#		promo.appendChild(doc.createTextNode('/home/pmo/Desktop/najjla/images/'+res[i]['image']))
#		doc.documentElement.appendChild(promo)
#
#	# fin de page de garde
#
#	products = doc.createElement('products')
#	doc.documentElement.appendChild(products)
#
#	if len(tab_avoid)>1:
#		where_avoid = "and ref not in "+str(tuple(tab_avoid))
#	if len(tab_avoid)==1:
#		where_avoid = " and ref!='"+str(tab_avoid[0])+"' "
#	else:
#		where_avoid = ''
#	side = 0
#	length = 0
##	print 'select * from aie_catalog where did=%s and lang=%s %s order by ref limit %s' % (where_avoid,did,lang,limit)
#	cr.execute('select * from auction_lots where did=%s and lang=%s '+where_avoid+' order by ref limit %s', (did,lang,limit))
#	res = cr.fetchall()
##	print res
#	for cat in res:
#		product = doc.createElement('product')
#		products.appendChild(product)
#
##TODO : Ajouter un test pour afficher l'artiste, ou pas
#		for key in ('ref','artist'):
#			ref = doc.createElement(key)
#			ref.appendChild(doc.createTextNode( escape(cat[key])))
#			product.appendChild(ref)
#
#		if cat['info']:
#			infos = doc.createElement('infos')
#			lines = re.split('<br/>|\n', cat['info'])
##			lines = cat['info'].splitlines()
#			for line in lines:
#				xline = doc.createElement('info')
#				xline.appendChild(doc.createTextNode(escape(line)))
#				infos.appendChild(xline)
#			product.appendChild(infos)
#
#		for key in ('est1','est2'):
#			ref = doc.createElement(key)
#			ref.appendChild(doc.createTextNode( escape(cat[key] or 0.0)))
#			product.appendChild(ref)
#
#		oldlength = length
#		if cat['photo'] and (cat['ref'] not in tab_no_photo):
#			dest = os.path.join('/tmp/pdf_catalog/',str(cwid),str(cat['ref'])+'.jpg')
#			if cat['ref'] not in dict_size.keys():
#				ref = doc.createElement('photo')
#				size = photo_shadow.convert_catalog('/home/pmo/Desktop/najjla/images/'+cat['image'], dest)
#			elif dict_size[cat['ref']]=='S':
#				ref = doc.createElement('photo_small')
#				size = photo_shadow.convert_catalog('/home/pmo/Desktop/najjla/images/'+cat['image'], dest, 110)
#			else :
#				ref = doc.createElement('photo_large')
#				size = photo_shadow.convert_catalog('/home/pmo/Desktop/najjla/images/'+cat['image'], dest, 440)
#			ref.appendChild(doc.createTextNode(dest))
#			product.appendChild(ref)
#			if size[1]>=size[0]:
#				length += 4.5
#			else:
#				length += (4.5 * size[1])/size[0]
#
#		else:
#			length += 2.0
#
#		length += 0.30
#
#		if length>23.7:
#			side += 1
#			length = length - oldlength
#			ref = doc.createElement('newpage')
#			ref.appendChild(doc.createTextNode( "1" ))
#			product.appendChild(ref)
#
#		if side%2:
#			ref = doc.createElement('side')
#			ref.appendChild(doc.createTextNode( "1" ))
#			product.appendChild(ref)
#
#	cr.close()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#        product_categ_id =pool.get('product.category').search(cr,uid,[])
#        currency = pool.get('product.pricelist').read(cr,uid,[price_list_id],['currency_id','name'])[0]
#
#        print ids
#        qty =[]
#
#        for i in range(1,6):
#            q = 'qty%d'%i
#            if data['form'][q]:
#                qty.append(data['form'][q])
#
#        if not qty:
#            qty.append(1)
#
#        product_xml = []
#        cols = ''
#        cols = cols+'6cm'
#        title ='<title name=" Description " number="0" />'
#        i=1
#        for q in qty:
#            cols = cols+',2.5cm'
#            if q==1:
#                title+='<title name="%d unit" number="%d"/>'%(q,i)
#            else:
#                title+='<title name="%d units" number="%d"/>'%(q,i)
#            i+=1
#        date = datetime.date.today()
#        str_date=date.strftime("%d/%m/%Y")
#        product_xml.append('<cols>'+cols+'</cols>')
#        product_xml.append('<pricelist> %s </pricelist>'%currency['name'])
#        product_xml.append('<currency> %s </currency>'%currency['currency_id'][1])
#        product_xml.append('<date> %s </date>'%str_date)
#        product_xml.append("<product>")
#
#        for p_categ_id in product_categ_id:
#            product_ids = pool.get('product.product').search(cr,uid,[('id','in',ids),('categ_id','=',p_categ_id)])
#            if product_ids:
#                categ_name = pool.get('product.category').read(cr,uid,[p_categ_id],['name'])
#                products = pool.get('product.product').read(cr,uid,product_ids,['name','code'])
#                price_list = []
#                for i in product_ids:
#                    price_dict = pool.get('product.pricelist').price_get(cr,uid,[price_list_id],i,1)
#                    if price_dict[price_list_id]:
#                        price = price_dict[price_list_id]
#                    else:
#                        res = pool.get('product.product').read(cr, uid,[i])
#                        price =  res[0]['list_price']
#                    price_list.append({i:price})
##                categ = []
##                categ.append('<categ name="%s">' % ( categ_name[0]['name']))
#                pro = []
#                i=0
#                pro.append('<pro name="%s" categ="true">' % (categ_name[0]['name']))
#                temp = []
#                for q in qty:
#                    temp.append('<price name=" " />')
#                pro.extend(temp)
#                pro.append('</pro>')
#                for x in products:
#                    if x['code']:
#                        pro.append('<pro name="[%s] %s" >' % (x['code'], x['name']))
#                    else:
#                        pro.append('<pro name="%s" >' % (x['name']))
#                    temp = []
#                    for q in qty:
##                        temp.append('<price name="%s %s" />'%(price_list[i][x['id']]*q[2]['name'],currency['currency_id'][1]))
#                        temp.append('<price name="%.2f" />'%(price_list[i][x['id']]*q))
#                    i+=1
#                    pro.extend(temp)
#                    pro.append('</pro>')
##                categ.extend(pro)
##                categ.append('</categ>')
#                product_xml.extend(pro)
#
#        product_xml.append('</product>')
#
#        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
#        <report>
#        %s
#        </report>
#        '''  % (title+'\n'.join(product_xml))
#        return self.post_process_xml_data(cr, uid, xml, context)
#
#report_custom('report.pricelist.pricelist', 'product.product','','addons/product/report/product_price.xsl')
