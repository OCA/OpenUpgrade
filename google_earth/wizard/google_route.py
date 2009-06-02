# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import urllib
import xml.dom.minidom
import base64

import wizard
import pooler
import tools
from osv import osv,fields

_earth_form =  '''<?xml version="1.0"?>
<form string="Google Map/Earth">
    <separator string="Select path to store KML file" colspan="2"/>
    <newline/>
    <field name="name"/>
    <newline/>
    <field name="kml_file"/>
</form>'''

_earth_fields = {
        'name': {'string': 'KML File name', 'type': 'char', 'readonly': False , 'required': True},
        'kml_file': {'string': 'Save KML file', 'type': 'binary', 'required': True},
            }

def geocode(address):
    mapsKey = 'abcdefgh'
    mapsUrl = 'http://maps.google.com/maps/geo?q='
    url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',mapsKey])
    coordinates = urllib.urlopen(url).read().split(',')
    coorText = '%s,%s' % (coordinates[3],coordinates[2])
    return coorText

def get_directions(source, destination):
    steps = []
    res = False
    try:
        from google.directions import GoogleDirections
        gd = GoogleDirections('ABQIAAAAUbF6J26EmcC_0QgBXb9xvhRoz3DfI4MsQy-vo3oSCnT9jW1JqxQfs5OWnaBY9or_pyEGfvnnRcWEhA')
        res = gd.query(source,destination)
    except:
        raise wizard.except_wizard('Warning!','Please install Google direction package from http://pypi.python.org/pypi/google.directions/0.3 ')

    if res:
        if res.status != 200:
            print "Address not found. Status was: %d" % res.status
            return
        if 'Directions' in res.result:
            endPoint = res.result['Directions']['Routes'][0]['End']['coordinates']
            result = res.result['Directions']['Routes'][0]['Steps']
            for i in result:
                steps.append(i['Point']['coordinates'])
            steps.append(endPoint)
            return steps

def _create_kml(self, cr, uid, data, context={}):
    #Todo:
    #    1. should be work with different country cities currenly it takes strait path if cities are in differnt countries
    #    2. should be test for all cities (Shanghai -> Hongkong ) check to upper and lower possiblities to search
    #    3. packages needed : google.directions-0.3.tar.gz

    #Note: from google.directions import GoogleDirections : this package shuld be install in order to run the wizard
#    path = tools.config['addons_path']
#    fileName = path + '/google_earth/kml/route.kml'
    colors = ['ff000080','ff800000','ff800080','ff808000','ff8080ff','ff80ff80','ffff8080','ffFACE87','ff1E69D','ff87B8DE', 'ff000000']
    pool = pooler.get_pool(cr.dbname)
    warehouse_obj = pool.get('stock.warehouse')
     #cr.execute('select sp.warehouse_id, sum(m.product_qty) as product_send, count(s.id) as number_delivery,a.city as customer_city from stock_picking as s left join sale_order as so on s.sale_id=so.id left join sale_shop as sp on so.shop_id=sp.id left join stock_warehouse as w on w.id=sp.warehouse_id left join stock_move as m on s.id=m.picking_id left join res_partner_address as a on a.id=s.address_id  left join res_partner as p on p.id=a.partner_id where sale_id is not null group by a.city,sp.warehouse_id;')


    #cr.execute('select sp.warehouse_id, sum(m.product_qty) as product_send, count(s.id) as number_delivery,a.city as customer_city, cc.name as customer_country from stock_picking as s left join sale_order as so on s.sale_id=so.id left join sale_shop as sp on so.shop_id=sp.id left join stock_warehouse as w on w.id=sp.warehouse_id left join stock_move as m on s.id=m.picking_id left join res_partner_address as a on a.id=s.address_id  left join res_partner as p on p.id=a.partner_id left join res_country as cc on a.country_id=cc.id where sale_id is not null group by a.city,cc.name,sp.warehouse_id;')
    cr.execute('select sp.warehouse_id, sum(m.product_qty) as product_send, count(s.id) as number_delivery,a.city as customer_city, cc.name as customer_country from stock_picking as s left join sale_order as so on s.sale_id=so.id left join sale_shop as sp on so.shop_id=sp.id left join stock_warehouse as w on w.id=sp.warehouse_id left join stock_move as m on s.id=m.picking_id left join res_partner_address as a on a.id=s.address_id  left join res_partner as p on p.id=a.partner_id left join res_country as cc on a.country_id=cc.id where sale_id is not null and a.city is not null and cc.name is not null group by a.city,cc.name,sp.warehouse_id')
    packings = cr.dictfetchall()
    warehouse_ids = warehouse_obj.search(cr, uid, [])
    warehouse_datas = warehouse_obj.browse(cr, uid, warehouse_ids)
    warehouse_dict = {}

    for whouse in warehouse_datas:
        warehouse_dict[whouse.id] = whouse.partner_address_id and whouse.partner_address_id.city or False

    if not packings:
        raise osv.except_osv('Warning !', 'You do not have deliveries available')
    no_of_packs_max = max(map(lambda x: x['number_delivery'], packings)) or 0
    no_of_packs_min = min(map(lambda x: x['number_delivery'], packings)) or 0

    value = (no_of_packs_max - no_of_packs_min)/10 # 25 50 75 100
    c1 = no_of_packs_min + value
    c2 = c1 + value
    c3 = c2 + value
    c4 = c3 + value
    c5 = c4 + value
    c6 = c5 + value
    c7 = c6 + value
    c8 = c7 + value
    c9 = c8 + value

    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://maps.google.com/kml/2.2','kml')
    kmlElement = kmlDoc.appendChild(kmlElement)

    documentElement = kmlDoc.createElement('Document')
    kmlElement.appendChild(documentElement)
    documentElementname = kmlDoc.createElement('name')
    documentElementname.appendChild(kmlDoc.createTextNode('Route'))
    documentElementdesc = kmlDoc.createElement('description')
#    documentElementdesc.appendChild(kmlDoc.createTextNode('When you click on locaion you will get path from warehouse location to customer location'))
    documentElementdesc.appendChild(kmlDoc.createTextNode(
    ' Color  :           Number of Delivery range \n' \
    '================================================================================================='
    ' Marun : ' + str(no_of_packs_min) + '-' + str(c1) + '\n' \
    ' Dark Blue : ' + str(c1+1) + '-' + str(c2) + '\n' \
    ' Purple : ' + str(c2+1) + '-' + str(c3) + '\n' \
    ' Dark green : ' + str(c3+1) + '-' + str(c4) + '\n' \
    ' Pink : ' + str(c4+1) + '-' + str(c5) + '\n' \
    ' Light green : ' + str(c5+1) + '-' + str(c6) + '\n' \
    ' violet : ' + str(c6+1) + '-' + str(c7) + '\n' \
    ' Sky blue : ' + str(c7+1) + '-' + str(c8) + ' \n' \
    ' orange : ' + str(c8+1) + '-' + str(c9) + '\n' \
    ' light brown: ' + '>' + str(c9+1) + '\n' \
    '=================================================================================================' \
    'Note: map display delivery route from warehouse location to customer locations(cities), it calculates number of deliveries by cities \n' \
    ))

    polystyleElement = kmlDoc.createElement('PolyStyle')
    fillElement = kmlDoc.createElement('fill')
    fillElement.appendChild(kmlDoc.createTextNode('1'))
    polystyleElement.appendChild(fillElement)
    outlineElement = kmlDoc.createElement('outline')
    outlineElement.appendChild(kmlDoc.createTextNode('1'))
    polystyleElement.appendChild(outlineElement)
    documentElement.appendChild(polystyleElement)
    documentElement.appendChild(documentElementname)
    documentElement.appendChild(documentElementdesc)
    line = ''
    for pack in packings:
        total_qty = pack['product_send']
        warehouse_city = warehouse_dict[pack['warehouse_id']]
        customer_city = pack['customer_city']
        customer_country = pack['customer_country']
        if not (warehouse_city and customer_city):
            raise wizard.except_wizard('Warning!','Address is not defiend on warehouse or customer. ')

        desc_text = '<html><head><font color="red" size=1.9><b> <table border=5 bordercolor="blue"><tr><td>  Warehouse location</td> <td>' + warehouse_city + '</td></tr><tr><td>' + line + '  Customer Location</td><td> ' + customer_city + ' ' + customer_country + '</td></tr><tr><td>' + line +' Number of product sent</td><td> ' + str(total_qty) + '</td></tr>' +  line +\
        ' <tr><td>Number of delivery</td><td> ' + str(pack['number_delivery']) + '</td></tr>' + '</table></b>  </font></head></html>'

        placemarkElement = kmlDoc.createElement('Placemark')
        placemarknameElement = kmlDoc.createElement('name')
        placemarknameText = kmlDoc.createTextNode(str(warehouse_city))
        placemarkdescElement = kmlDoc.createElement('description')
        placemarkdescElement.appendChild(kmlDoc.createTextNode(desc_text))
        placemarknameElement.appendChild(placemarknameText)
        placemarkElement.appendChild(placemarknameElement)
        placemarkElement.appendChild(placemarkdescElement)

        styleElement = kmlDoc.createElement('Style')
        placemarkElement.appendChild(styleElement)
        linestyleElement = kmlDoc.createElement('LineStyle')
        styleElement.appendChild(linestyleElement)
        colorElement = kmlDoc.createElement('color')
        if pack['number_delivery'] >= no_of_packs_min and pack['number_delivery'] <= c1:
            colorElement.appendChild(kmlDoc.createTextNode(colors[0]))
        elif pack['number_delivery'] > c1 and pack['number_delivery'] <= c2:
            colorElement.appendChild(kmlDoc.createTextNode(colors[1]))
        elif pack['number_delivery'] > c2 and pack['number_delivery'] <= c3:
            colorElement.appendChild(kmlDoc.createTextNode(colors[2]))
        elif pack['number_delivery'] > c3 and pack['number_delivery'] <= c4:
            colorElement.appendChild(kmlDoc.createTextNode(colors[3]))
        elif pack['number_delivery'] > c4 and pack['number_delivery'] <= c5:
            colorElement.appendChild(kmlDoc.createTextNode(colors[4]))
        elif pack['number_delivery'] > c5 and pack['number_delivery'] <= c6:
            colorElement.appendChild(kmlDoc.createTextNode(colors[5]))
        elif pack['number_delivery'] > c6 and pack['number_delivery'] <= c7:
            colorElement.appendChild(kmlDoc.createTextNode(colors[6]))
        elif pack['number_delivery'] > c7 and pack['number_delivery'] <= c8:
            colorElement.appendChild(kmlDoc.createTextNode(colors[7]))
        elif pack['number_delivery'] > c8 and pack['number_delivery'] <= c9:
            colorElement.appendChild(kmlDoc.createTextNode(colors[8]))
        else:
            colorElement.appendChild(kmlDoc.createTextNode(colors[9]))

        widthElement = kmlDoc.createElement('width')
        widthElement.appendChild(kmlDoc.createTextNode('4'))

        linestyleElement.appendChild(colorElement)
        linestyleElement.appendChild(widthElement)

        lineElement = kmlDoc.createElement('LineString')
        placemarkElement.appendChild(lineElement)

        coorElement = kmlDoc.createElement('coordinates')
        lineElement.appendChild(coorElement)

        steps = get_directions(warehouse_city, customer_city)
        if not steps: # make route path strait
            coordinates1 = geocode(warehouse_city)
            coordinates2 = geocode(customer_city)
            coordinates2 = coordinates2 + '\n'
#            coordinates1 = coordinates1 + '\n'
            coorElement.appendChild(kmlDoc.createTextNode(coordinates2))
            coorElement.appendChild(kmlDoc.createTextNode(coordinates1))
#            coordinates2 = geocode(customer_city)
#            coorElement.appendChild(kmlDoc.createTextNode(coordinates2))
        else:
            for s in steps:
                coorText = '%s, %s, %s \n' % (s[0], s[1], s[2])
                coorElement.appendChild(kmlDoc.createTextNode(coorText))

        lineElement.appendChild(coorElement)
        documentElement.appendChild(placemarkElement)
    out = base64.encodestring(kmlDoc.toxml())
    fname = 'route' + '.kml'
    return {'kml_file': out, 'name': fname}

class delivery_route(wizard.interface):

    states = {
       'init': {
            'actions': [_create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                },
            }
delivery_route('google.find.route')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: