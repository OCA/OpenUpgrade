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
import os, xml, string
import urllib
import xml.dom.minidom
from xml.dom.minidom import parse, parseString

import wizard
import pooler
import tools

_earth_form =  '''<?xml version="1.0"?>
        <form string="Google Map/Earth">
        <label string="kml file created in ../google_earth/kml/partner_region.kml"/>
        </form> '''

_earth_fields = {
            }


def geocode(address):
    # This function queries the Google Maps API geocoder with an
    # address. It gets back a csv file, which it then parses and
    # returns a string with the longitude and latitude of the address.

    # This isn't an actual maps key, you'll have to get one yourself.
    # Sign up for one here: http://code.google.com/apis/maps/signup.html
    mapsKey = 'abcdefgh'
    mapsUrl = 'http://maps.google.com/maps/geo?q='

    # This joins the parts of the URL together into one string.
    url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',mapsKey])

    # This retrieves the URL from Google.
    coordinates = urllib.urlopen(url).read().split(',')

    # This parses out the longitude and latitude, and then combines them into a string.
    coorText = '%s,%s' % (coordinates[3],coordinates[2])
    return coorText

def create_kml(self, cr, uid, data, context={}):
    #Todo:
    #    check for all countries working with google or not (India..)
    # This function creates an XML document and adds the necessary
    # KML elements.
    res = {}
    address = ' '
    coordinates = []
    addresslist = []
    country_list = []
    coordinates_text = ' '

    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    address_obj= pool.get('res.partner.address')
    path = tools.config['addons_path']
    fileName = path + '/google_earth/kml/partner_region.kml'
    partner_ids = partner_obj.search(cr, uid, [])
    partners = partner_obj.browse(cr, uid, partner_ids)

    for part in partners:
        #Todo: should be check for contact/defualt type address
        if part.address and part.address[0].country_id and part.address[0].country_id.name:
            if not string.upper(part.address[0].country_id.name) in country_list:
                cntry = string.upper(str(part.address[0].country_id.name))
                country_list.append(cntry)

    map(lambda x:res.setdefault(x,0.0), country_list)
    # fetch turnover by country
    cr.execute('select sum(l.credit), c.name from account_move_line as l join res_partner_address as a on l.partner_id=a.partner_id left join res_country as c on c.id=a.country_id group by c.name')
    res_partner = cr.fetchall()
    for part in res_partner:
        res[string.upper(part[1])] = part[0]

    # fetch turnover by individual partner
    cr.execute('select min(id) as id, sum(credit) as turnover, partner_id as partner_id from account_move_line group by partner_id')
    res_partner = cr.fetchall()
    for part in partners:
        for id, turnover, partner_id in res_partner:
            if not (partner_id == part.id):
                res[part.id] = 0
            if partner_id == part.id:
                res[part.id] = turnover

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

    for part in partners:
        address = ''
        add = address_obj.browse(cr, uid, part.address and part.address[0].id, context) # Todo: should be work for multiple address
        if add:
            if add.street:
                address += str(add.street)
            if add.street2:
                address += ', '
                address += str(add.street2)
            if add.city:
                address += ', '
                address += str(add.city)
            if add.state_id:
                address += ', '
                address += str(add.state_id.name)
            if add.country_id:
                address += ', '
                address += str(add.country_id.name)

        desc_text = address + ' , turnover of partner : ' + str(res[part.id])
        placemarkElement = kmlDoc.createElement('Placemark')
        placemarknameElement = kmlDoc.createElement('name')
        placemarknameText = kmlDoc.createTextNode(part.name)
        placemarknameElement.appendChild(placemarknameText)
        placemarkElement.appendChild(placemarknameElement)
        descriptionElement = kmlDoc.createElement('description')
        descriptionText = kmlDoc.createTextNode(desc_text)
        descriptionElement.appendChild(descriptionText)
        placemarkElement.appendChild(descriptionElement)
        pointElement = kmlDoc.createElement('Point')
        placemarkElement.appendChild(pointElement)
        coorElement = kmlDoc.createElement('coordinates')
        # This geocodes the address and adds it to a <Point> element.
        coordinates = geocode(address)
        coorElement.appendChild(kmlDoc.createTextNode(coordinates))
        pointElement.appendChild(coorElement)
        documentElement.appendChild(placemarkElement)

    documentElement = kmlElement.appendChild(documentElement)
    documentElementname = kmlDoc.createElement('name')
    documentElementname.appendChild(kmlDoc.createTextNode('Todo name'))
    documentElementdesc = kmlDoc.createElement('description')
    documentElementdesc.appendChild(kmlDoc.createTextNode('Todo desctiption'))

    documentElement.appendChild(documentElementname)
    documentElement.appendChild(documentElementdesc)

    styleElement = kmlDoc.createElement('Style')
    styleElement.setAttribute('id','transBluePoly')

    linestyleElement = kmlDoc.createElement('LineStyle')
    colorElement = kmlDoc.createElement('color')
    colorElement.appendChild(kmlDoc.createTextNode('CC66CC'))
    linestyleElement.appendChild(colorElement)
    styleElement.appendChild(linestyleElement)
    ballonElement = kmlDoc.createElement('BalloonStyle')
    ballonbgElement = kmlDoc.createElement('bgColor')
    ballonbgElement.appendChild(kmlDoc.createTextNode('59009900'))
    balloontextElement = kmlDoc.createElement('text')
    balloontextElement.appendChild(kmlDoc.createTextNode('TESSTT'))
    ballonElement.appendChild(ballonbgElement)
    ballonElement.appendChild(balloontextElement)
    styleElement.appendChild(ballonElement)

    polystyleElement = kmlDoc.createElement('PolyStyle')
    polycolorElement = kmlDoc.createElement('color')
    polycolorElement.appendChild(kmlDoc.createTextNode('FF0000'))
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

    #different color should be used
    colors = ['33333333','dfbf9f3b','59009900','FF9933','FF3300','FF66CC','993399','00FF33','CC99CC','FF0000','CC66CC','6633CC','00FF99','990099','0099FF','CCCCFF','CCCC99','66CCFF','00CCFF','CC9933','FFCC99','CCCC66','99FF33']
    len_color = len(colors)
    cnt = 0
    for country in country_list:
        cnt += 1 #should be used
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
        placemarkcolorrElement.appendChild(kmlDoc.createTextNode('FF0000'))#colors[cnt])
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