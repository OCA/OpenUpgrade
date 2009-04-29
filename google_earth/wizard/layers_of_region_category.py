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

import wizard
import pooler
import tools
from osv import osv, fields


_earth_form =  '''<?xml version="1.0"?>
        <form string="Google Map/Earth">
        <separator string="Select Partner" colspan="4"/>
        <field name="partner_id"/>
        </form> '''

_earth_fields = {
            'partner_id': {'string': 'Partner', 'type': 'many2one', 'relation': 'res.partner', 'required': True,},
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
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    path = tools.config['addons_path']
    fileName = path + '/google_earth/kml/partner_region.kml'
    partner_data = partner_obj.browse(cr, uid, data['form']['partner_id'], context)

#    cr.execute('select min(id) as id, sum(credit) as turnover, partner_id as partner_id from account_move_line group by partner_id')
##    for id, turnover, partner_id in cr.fetchall():
##        if not (partner_id == data['form']['partner_id']):
##            raise wizard.except_wizard('Warning','This parnter has no turnover')
##            return {}
    address_obj= pool.get('res.partner.address')
    add = address_obj.browse(cr, uid, partner_data.address[0].id, context) # Todo: should be work for multiple address

    if add.city:
        address += str(add.city)
    if add.state_id:
        address += ', '
        address += str(add.state_id.name)
    if add.country_id:
        address += ', '
        address += str(add.country_id.name)

    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://maps.google.com/kml/2.2','kml')
    kmlElement = kmlDoc.appendChild(kmlElement)

    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)

    RegionElement = kmlDoc.createElement('Region')

    LatlonaltboxElement = kmlDoc.createElement('LatLonAltBox')
    northElement = kmlDoc.createElement('north')
    LatlonaltboxElement.appendChild(northElement)
    southElement = kmlDoc.createElement('south')
    LatlonaltboxElement.appendChild(southElement)
    eastElement = kmlDoc.createElement('east')
    LatlonaltboxElement.appendChild(eastElement)
    westElement = kmlDoc.createElement('west')
    LatlonaltboxElement.appendChild(westElement)
    RegionElement.appendChild(LatlonaltboxElement)

    LodElement = kmlDoc.createElement('Lod')
    minlodpixelsElement = kmlDoc.createElement('minLodPixels')
    LodElement.appendChild(minlodpixelsElement)
    maxlodpixelsElement = kmlDoc.createElement('maxLodPixels')
    LodElement.appendChild(maxlodpixelsElement)
    RegionElement.appendChild(LodElement)

    documentElement.appendChild(RegionElement)

    placemarkElement = kmlDoc.createElement('Placemark')

    placemarknameElement = kmlDoc.createElement('name')
    placemarknameText = kmlDoc.createTextNode(partner_data.name)
    placemarknameElement.appendChild(placemarknameText)
    placemarkElement.appendChild(placemarknameElement)

    descriptionElement = kmlDoc.createElement('description')
    descriptionText = kmlDoc.createTextNode(address)
    descriptionElement.appendChild(descriptionText)
    placemarkElement.appendChild(descriptionElement)

    linestringElement = kmlDoc.createElement('LineString')
    tessellateElement = kmlDoc.createElement('tessellate')
    tessellateText = kmlDoc.createTextNode('1')
    tessellateElement.appendChild(tessellateText)
    linestringElement.appendChild(tessellateElement)
    coordinatesElement = kmlDoc.createElement('coordinates')
    linestringElement.appendChild(coordinatesElement)
    placemarkElement.appendChild(linestringElement)

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
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Cancel'),('map','Get map')]}
                },
         'map': {
            'actions': [create_kml],
            'result': {'type': 'state', 'state': 'end'}
                }
            }
customer_on_map('layers.region.catery')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: