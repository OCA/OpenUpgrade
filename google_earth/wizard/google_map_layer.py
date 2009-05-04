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
#import arcgisscripting,
import datetime, os, zipfile, xml, string
from xml.dom.ext.reader.Sax2 import FromXmlStream
from xml.dom.ext import PrettyPrint

import urllib
import xml.dom.minidom
import pyexpat
#from xml.sax import ExpatParser

import wizard
import pooler
import tools
from osv import osv, fields


_earth_form =  '''<?xml version="1.0"?>
        <form string="Google Map/Earth" >
        <separator string="Enter Region(city/state/country)" colspan="4" />
        <newline/>
        <field name="region" help="wizard will create kml files using that kml file you can see the all partners which contains the given region for e.g if you enter India you can see all partners in india on google map within layer"/>
        </form> '''

_earth_fields = {
            'region': {'string': 'Region', 'type': 'char','required': True,},
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
    # This function creates an XML document and adds the necessary
    # KML elements.

    address = ' '
    coordinates = []
    addresslist = []
    coordinates_text = ' '
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    path = tools.config['addons_path']
    fileName = path + '/google_earth/kml/partner_region.kml'
    address_obj= pool.get('res.partner.address')
    address_with_country_ids = address_obj.search(cr, uid, [('country_id.name','=', data['form']['region'])])
    address_with_state_ids = address_obj.search(cr, uid, [('state_id.name','=', data['form']['region'])])
    address_with_city_ids = address_obj.search(cr, uid, [('city','=', data['form']['region'])])

    if address_with_country_ids:
        for id in address_with_country_ids:
            add = address_obj.browse(cr, uid, id, context)
            address = ' '
            if add.city:
                address += str(add.city)
            if add.state_id:
                address += ', '
                address += str(add.state_id.name)
            if add.country_id:
                address += ', '
                address += str(add.country_id.name)
            addresslist.append(address)
    elif address_with_state_ids:
        for id in address_with_state_ids:
            add = address_obj.browse(cr, uid, id, context)
            address = ' '
            if add.city:
                address += str(add.city)
            if add.state_id:
                address += ', '
                address += str(add.state_id.name)
            if add.country_id:
                address += ', '
                address += str(add.country_id.name)
            addresslist.append(address)
    elif address_with_city_ids:
        for id in address_with_city_ids:
            add = address_obj.browse(cr, uid, id, context)
            address = ' '
            if add.city:
                address += str(add.city)
            if add.state_id:
                address += ', '
                address += str(add.state_id.name)
            if add.country_id:
                address += ', '
                address += str(add.country_id.name)
            addresslist.append(address)
    else:
        raise wizard.except_wizard('Warning','Region has not defined')
        return {}

    for add in addresslist:
        coordinates.sort(coordinates.append(geocode(add)))
    for coordinate in coordinates:
        coordinates_text += coordinate + '\n\t'

#    kml creation start
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2','kml')
    kmlElement.setAttribute('xmlns','http://www.opengis.net/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)

    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)

    styleElement = kmlDoc.createElement('Style')
#    styleElement = kmlDoc.EndElement(style)
    styleElement.setAttribute('id','transBluePoly')

    linestyleElement = kmlDoc.createElement('LineStyle')
#    colorElement = kmlDoc.createElement('color')
#    colorElement.appendChild(kmlDoc.createTextNode('80000000'))
#    linestyleElement.appendChild(colorElement)
    widthElement = kmlDoc.createElement('width')
    widthElement.appendChild(kmlDoc.createTextNode('1.5'))
    linestyleElement.appendChild(widthElement)
    styleElement.appendChild(linestyleElement)

    polystyleElement = kmlDoc.createElement('PolyStyle')
    polycolorElement = kmlDoc.createElement('color')
    polycolorElement.appendChild(kmlDoc.createTextNode('59009900'))
    polystyleElement.appendChild(polycolorElement)
#    fillElement = kmlDoc.createElement('fill')
#    fillElement.appendChild(kmlDoc.createTextNode('1'))
#    polystyleElement.appendChild(fillElement)
#    outlineElement = kmlDoc.createElement('outline')
#    outlineElement.appendChild(kmlDoc.createTextNode('1'))
#    polystyleElement.appendChild(outlineElement)
    styleElement.appendChild(polystyleElement)
    documentElement.appendChild(styleElement)

    placemarkElement = kmlDoc.createElement('Placemark')
    placemarknameElement = kmlDoc.createElement('name')
    placemarknameText = kmlDoc.createTextNode(data['form']['region'])
    placemarknameElement.appendChild(placemarknameText)
    placemarkElement.appendChild(placemarknameElement)
#    descriptionElement = kmlDoc.createElement('description')
#    desc = """<![CDATA[Terre Haute City Council<br>District 4<br>Councilman: Todd Nation<br>
#    website: <a href="http://www.toddnation.com">toddnation.com</a>]]>"""
#    cdataElement = kmlDoc.createElement('![CDATA[')
#    descriptionElement.appendChild(cdataElement)
#    descriptionText = kmlDoc.createTextNode(desc)
#    descriptionElement.appendChild(descriptionText)
#    placemarkElement.appendChild(descriptionElement)
    styleurlElement = kmlDoc.createElement('styleUrl')
    styleurlElement.appendChild(kmlDoc.createTextNode('#transBluePoly'))
    placemarkElement.appendChild(styleurlElement)
    polygonElement = kmlDoc.createElement('Polygon')

    extrudeElement = kmlDoc.createElement('extrude')
    extrudeElement.appendChild(kmlDoc.createTextNode('1'))
    polygonElement.appendChild(extrudeElement)

    altitudemodeElement = kmlDoc.createElement('altitudeMode')
    altitudemodeElement.appendChild(kmlDoc.createTextNode('relativeToGround'))
    polygonElement.appendChild(altitudemodeElement)

    outerboundaryisElement = kmlDoc.createElement('outerBoundaryIs')
    linearringElement = kmlDoc.createElement('LinearRing')

#    tessellateElement = kmlDoc.createElement('tessellate')
#    tessellateElement.appendChild(kmlDoc.createTextNode('1'))
#    linearringElement.appendChild(tessellateElement)

    coordinatesElemenent = kmlDoc.createElement('coordinates')
    coordinatesElemenent.appendChild(kmlDoc.createTextNode(coordinates_text))
    linearringElement.appendChild(coordinatesElemenent)

    outerboundaryisElement.appendChild(linearringElement)
    polygonElement.appendChild(outerboundaryisElement)
    placemarkElement.appendChild(polygonElement)

    documentElement.appendChild(placemarkElement)

    # This writes the KML Document to a file.
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toprettyxml(' '))
    kmlFile.close()
    return {}

class customer_on_map(wizard.interface):

    states = {
       'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Cancel'),('map','Get Partners on map')]}
                },
         'map': {
            'actions': [create_kml],
            'result': {'type': 'state', 'state': 'end'}
                }
            }
customer_on_map('layers.region.catery')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: