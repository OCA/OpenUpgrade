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
import base64

def escape(s):
    return str(s or '').replace('<br/>','').decode('latin1','replace').encode('utf-8')


class auction_catalog(report_rml):

    def create_xml(self, cr, uid, ids, data, context):

        xml = self.catalog_xml(cr, uid, ids, data, context)
        #return self.post_process_xml_data(cr, uid, xml, context)
        print "********************************************"
        temp=self.post_process_xml_data(cr, uid, xml, context)
#        print temp
        print "********************************************",temp

        return temp
    def catalog_xml(self,cr,uid,ids,data,context):
        impl = minidom.getDOMImplementation()

        doc = impl.createDocument(None, "report", None)

        #catalog element
        catalog=doc.createElement('catalog')
        doc.documentElement.appendChild(catalog)


        infodb='info'
        commdb='comm'
        tab_avoid = []
        tab_no_photo=[]


 #     self.pool.get('auction.lots').search(self.cr,self.uid,([('auction_id','=',auction_id)]))
        ab=pooler.get_pool(cr.dbname).get('auction.lots').read(cr,uid,ids,['auction_id','name','image','lot_num','lot_est1','lot_est2'],context)

        print "AB::::::::::::",ab[0]['name']

        auction_dates_ids = [x["auction_id"][0] for x in ab]
        res=pooler.get_pool(cr.dbname).get('auction.dates').read(cr,uid,auction_dates_ids,['name','auction1','auction2'],context)

        # name emelment
        key = 'name'
        categ = doc.createElement(key)
        categ.appendChild(doc.createTextNode(escape(res[0]["name"])))
        catalog.appendChild(categ)

         #Auctuion Date element
        categ = doc.createElement("AuctionDate1")
        categ.appendChild(doc.createTextNode(escape(res[0]['auction1'])))
        catalog.appendChild(categ)

        # Action Date 2 element
        categ = doc.createElement("AuctionDate2")
        categ.appendChild(doc.createTextNode(escape(res[0]['auction2'])))
        catalog.appendChild(categ)



         # promotion element
        promo = doc.createElement('promotion1')

        fp = file('/home/pmo/Desktop/najjla/images/lj8100.jpg','r')
        file_data = fp.read()

        promo.appendChild(doc.createTextNode(base64.encodestring(file_data)))
        catalog.appendChild(promo)

        promo = doc.createElement('promotion2')

        fp = file('/home/pmo/Desktop/najjla/images/aeko_logo.jpg','r')
        file_data = fp.read()

        promo.appendChild(doc.createTextNode(base64.encodestring(file_data)))
        catalog.appendChild(promo)


        #product element
        products = doc.createElement('products')
        catalog.appendChild(products)

        side = 0
        length = 0

        cr.execute('select * from auction_lots where auction_id = 1')
        res = cr.dictfetchall()
        print "rESSSSSSSSS",res

        for cat in res:
            print "CAT:::::",cat
            product =doc.createElement('product')
            products.appendChild(product)

#            lot_num = doc.createElement('lot_num')
#            lot_num.appendChild(doc.createTextNode(escape(ab[0]['lot_num'])))
#            product.appendChild(lot_num)
#
#            lot_img = doc.createElement('Image')
#            lot_img.appendChild(doc.createTextNode(ab[0]['image']))
#            product.appendChild(lot_img)





            if cat['name']:
                infos = doc.createElement('infos')
                lines = re.split('<br/>|\n', cat['name'])
    #            lines = cat['info'].splitlines()

                print "lines:::::::::",lines

                for line in lines:
                    print  "LINE:::::::",line
                    xline = doc.createElement('info')
                    xline.appendChild(doc.createTextNode(escape(line)))
                    infos.appendChild(xline)
                product.appendChild(infos)

                if cat['lot_num']:
                    lnum = doc.createElement('lot_num')
                    lnum.appendChild(doc.createTextNode(escape(cat['lot_num'])))
                    infos.appendChild(lnum)

#                if cat['image']:
#                    limg = doc.createElement('Image')
#                    limg.appendChild(doc.createTextNode(cat['image']))
#                    infos.appendChild(limg)



            if ab[0]['image']:
                print "type of image::::::::",type(ab[0]['image'])
                lot_img = doc.createElement('Image')
                #abc=(ab[0]['image'])
                #print "VALUE OF ABC",type(abc)
                lot_img.appendChild(doc.createTextNode((ab[0]['image'])))

                product.appendChild(lot_img)



            for key in ('lot_est1','lot_est2'):

                ref2 = doc.createElement(key)
                ref2.appendChild(doc.createTextNode( escape(cat[key] or 0.0)))
                product.appendChild(ref2)

            oldlength = length
            length += 2.0


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
#        print "*************************"
#        print "generated : \n", xml1
#
#
##            print "TYPE OF XML",xml
#    #        print "Modified xml \n",type xml

        return xml1
auction_catalog('report.auction.cat_flagy', 'auction.lots','','addons/auction/report/catalog2.xsl')

