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

import sys
import datetime, os, zipfile, xml, string
from xml.dom.ext.reader.Sax2 import FromXmlStream
from xml.dom.ext import PrettyPrint

import urllib
import xml.dom.minidom
import pyexpat

import wizard
import pooler
import tools
from osv import osv, fields

_earth_form =  '''<?xml version="1.0"?>
        <form string="Google Map/Earth">
        <label string="kml file created in ../google_earth/kml/partner_region.kml"/>
        </form> '''

_earth_fields = {
            }


def create_kml(self, cr, uid, data, context={}):
    # This function creates an XML document and adds the necessary
    # KML elements.
    res = {}
    address = ' '
    coordinates = []
    addresslist = []
    coordinates_text = ' '
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    path = tools.config['addons_path']
    fileName = path + '/google_earth/kml/partner_region.kml'
    partner_ids = partner_obj.search(cr, uid, [])
    partners = partner_obj.browse(cr, uid, partner_ids)
    country_list = []
    for part in partners:
        #Todo: should be check for contact/defualt type address
        if part.address and part.address[0].country_id and part.address[0].country_id.name:
            if not string.upper(part.address[0].country_id.name) in country_list:
                cntry = string.upper(str(part.address[0].country_id.name))
                country_list.append(cntry)


    map(lambda x:res.setdefault(x,0.0), country_list)
    cr.execute('select sum(l.credit), c.name from account_move_line as l join res_partner_address as a on l.partner_id=a.partner_id left join res_country as c on c.id=a.country_id group by c.name')
    res_partner = cr.fetchall()
    for part in res_partner:
        res[string.upper(part[1])] = part[0]

    from xml.dom.minidom import parse, parseString
    ad = tools.config['addons_path'] # check for base module path also
    module_path = os.path.join(ad, 'google_earth/world_country.kml')
    dom1 = parse(module_path) # parse an XML file by name
    placemarks = dom1.getElementsByTagName('Placemark')
    dict_country = {}
    for place in placemarks:
        name = place.getElementsByTagName('name')
        value_name = " ".join(t.nodeValue for t in name[0].childNodes if t.nodeType == t.TEXT_NODE)
        cord = place.getElementsByTagName('coordinates')
        value_cord = " ".join(t.nodeValue for t in cord[0].childNodes if t.nodeType == t.TEXT_NODE)
        if value_name in country_list:
            dict_country[value_name] = value_cord

    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2','kml')
    kmlElement.setAttribute('xmlns','http://www.opengis.net/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)

    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)

    documentElement1 = kmlDoc.createElement('name')
    nameText1 = documentElement1.appendChild(kmlDoc.createTextNode('TEST'))
    documentElement22 = kmlDoc.createElement('description')
    desc22 = documentElement22.appendChild(kmlDoc.createTextNode('DESCripition'))

    documentElement.appendChild(documentElement1)
    documentElement.appendChild(documentElement22)

    styleElement = kmlDoc.createElement('Style')
#    styleElement = kmlDoc.EndElement(style)
    styleElement.setAttribute('id','transBluePoly')

    linestyleElement = kmlDoc.createElement('LineStyle')
    colorElement = kmlDoc.createElement('color')
    colorElement.appendChild(kmlDoc.createTextNode('cc000000'))
    linestyleElement.appendChild(colorElement)
    styleElement.appendChild(linestyleElement)
    ballonElement = kmlDoc.createElement('BalloonStyle')
    ballonbgElement = kmlDoc.createElement('bgColor')
    ballonbgElement.appendChild(kmlDoc.createTextNode('ffffffff'))
    balloontextElement = kmlDoc.createElement('text')
    balloontextElement.appendChild(kmlDoc.createTextNode('TESSTT'))
    ballonElement.appendChild(ballonbgElement)
    ballonElement.appendChild(balloontextElement)
    styleElement.appendChild(ballonElement)

    polystyleElement = kmlDoc.createElement('PolyStyle')
    polycolorElement = kmlDoc.createElement('color')
    polycolorElement.appendChild(kmlDoc.createTextNode('CC99CC'))
    polyfillElement = kmlDoc.createElement('fill')
    polyfillElement.appendChild(kmlDoc.createTextNode('1'))
    polyoutlineElement = kmlDoc.createElement('outline')
    polyoutlineElement.appendChild(kmlDoc.createTextNode('1'))

    polystyleElement.appendChild(polycolorElement)
    polystyleElement.appendChild(polyfillElement)
    polystyleElement.appendChild(polyoutlineElement)
    styleElement.appendChild(polystyleElement)
    documentElement.appendChild(styleElement)

    folderElement = kmlDoc.createElement('Folder')
    foldernameElement = kmlDoc.createElement('name')
    foldernameElement.appendChild(kmlDoc.createTextNode('Folder'))
    folderElement.appendChild(foldernameElement)

    colors = ['33333333','dfbf9f3b','59009900','FF9933','FF3300','FF66CC','993399','00FF33','CC99CC','FF0000','CC66CC','6633CC','00FF99','990099','0099FF','CCCCFF','CCCC99','66CCFF','00CCFF','CC9933','FFCC99','CCCC66','99FF33']
    len_color = len(colors)
    cnt = 0
    for country in country_list:
        cnt += 1
        cooridinate = dict_country[country]

        placemarkElement = kmlDoc.createElement('Placemark')
        placemarknameElement = kmlDoc.createElement('name')
        placemarknameText = kmlDoc.createTextNode(country)
        placemarkdescElement = kmlDoc.createElement('description')
        placemarkdescElement.appendChild(kmlDoc.createTextNode('Turnover of country: ' + str(res[country])))
        placemarknameElement.appendChild(placemarknameText)

        placemarkstyleElement = kmlDoc.createElement('Style')
        placemarkpolystyleElement = kmlDoc.createElement('PolyStyle')
        placemarkcolorrElement = kmlDoc.createElement('color')
        print colors[cnt]
        placemarkcolorrElement.appendChild(kmlDoc.createTextNode(colors[cnt]))
        placemarkpolystyleElement.appendChild(placemarkcolorrElement)
        placemarkstyleElement.appendChild(placemarkpolystyleElement)

        placemarkElement.appendChild(placemarknameElement)
        placemarkElement.appendChild(placemarkdescElement)
        placemarkElement.appendChild(placemarkstyleElement)

        styleurlElement = kmlDoc.createElement('styleUrl')
        styleurlElement.appendChild(kmlDoc.createTextNode('#transBluePoly'))
        placemarkElement.appendChild(styleurlElement)

        geometryElement = kmlDoc.createElement('MultiGeometry')
        polygonElement = kmlDoc.createElement('Polygon')

        outerboundaryisElement = kmlDoc.createElement('outerBoundaryIs')
        linearringElement = kmlDoc.createElement('LinearRing')

        coordinatesElemenent = kmlDoc.createElement('coordinates')
        coordinatesElemenent.appendChild(kmlDoc.createTextNode(cooridinate))
        linearringElement.appendChild(coordinatesElemenent)

        outerboundaryisElement.appendChild(linearringElement)
        polygonElement.appendChild(outerboundaryisElement)
        geometryElement.appendChild(polygonElement)
        placemarkElement.appendChild(geometryElement)

        folderElement.appendChild(placemarkElement)
        documentElement.appendChild(folderElement)

    # This writes the KML Document to a file.
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toxml())
    kmlFile.close()
    return {}

class customer_on_map(wizard.interface):
    states = {
         'init': {
            'actions': [create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                }
            }
customer_on_map('layers.region.catery')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: