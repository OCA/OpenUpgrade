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
        try:
            print "DATA::::::::::::::::::::::::::",data
            xml = self.catalog_xml(cr, uid, ids, data, context)
            print "after catch xml ::::::::::::::::",xml
        except e:
            print "Exception caught:::::",e
        return self.post_process_xml_data(cr, uid, xml, context)

    def catalog_xml(self,cr,uid,ids,data,context):
        impl = minidom.getDOMImplementation()
        doc = impl.createDocument(None, "catalog", None)
        infodb='info'
        commdb='comm'
        tab_avoid = []
        tab_no_photo=[]


 #     self.pool.get('auction.lots').search(self.cr,self.uid,([('auction_id','=',auction_id)]))
        ab=pooler.get_pool(cr.dbname).get('auction.lots').read(cr,uid,ids,['auction_id'],context)
        try:

            print " VALUE OF AB",ab
            auction_dates_ids = [x["auction_id"][0] for x in ab]
            print " VAKLUE IO AYCTUIH_DATES", auction_dates_ids
            res=pooler.get_pool(cr.dbname).get('auction.dates').read(cr,uid,auction_dates_ids,['name','auction1','auction2'],context)
            print " auction_date resporces",res;

            key = 'name'
            categ = doc.createElement(key)
            print "categ:::::::::::::::",categ
            print "catelog$$$$$$$$",categ,res[0]["name"]
            categ.appendChild(doc.createTextNode(escape(res[0]["name"])))
            print "categ:::::::::::::::",categ
            doc.documentElement.appendChild(categ)
            print "THE RES$$$$$$$$$$$$$",res[0]['auction1']

            categ = doc.createElement("AuctionDate1")
            print "categ:::::::::::::::",categ
            categ.appendChild(doc.createTextNode(escape(res[0]['auction1'])))
            print "categ:::::::::::::::",categ
            doc.documentElement.appendChild(categ)
            categ = doc.createElement("AuctionDate2")
            print "categ:::::::::::::::",categ
            categ.appendChild(doc.createTextNode(escape(res[0]['auction2'])))
            doc.documentElement.appendChild(categ)
            print "categ:::::::::::::::",categ



            promo = doc.createElement('promotion1')
            promo.appendChild(doc.createTextNode('/home/pmo/Desktop/auction_belgium4.1.1/auction_project/bin/images/crm.jpg'))
            doc.documentElement.appendChild(promo)

            products = doc.createElement('products')
            doc.documentElement.appendChild(products)

            side = 0
            length = 0

            cr.execute('select * from auction_lots where auction_id = 1')
            res = cr.dictfetchall()

            print "#################RES",
            for cat in res:
                product =doc.createElement('product')
                products.appendChild(product)



                if cat['name']:
                    infos = doc.createElement('infos')
                    lines = re.split('<br/>|\n', cat['name'])
        #            lines = cat['info'].splitlines()

                    print "LINESSSSSSSSSSSSSSS",lines
                    for line in lines:
                        xline = doc.createElement('info')
                        xline.appendChild(doc.createTextNode(escape(line)))
                        infos.appendChild(xline)
                    product.appendChild(infos)

                for key in ('lot_est1','lot_est2'):
                    print "Trueeeeeeee"
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
            #print "generated : \n", xml1

            xml = '<?xml version="1.0" ?><report>'+xml1[22:]+'</report>'

            print "TYPE OF XML",xml
    #        print "Modified xml \n",type xml
        except e:
            print "Exception caught:::::",e
        return xml
auction_catalog('report.auction.cat_flagy', 'auction.lots','','addons/auction/report/catalog2.xsl')

