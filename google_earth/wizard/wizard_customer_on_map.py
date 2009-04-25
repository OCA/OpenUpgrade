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

import wizard
from osv import osv
import pooler
import tools
from osv import fields

import urllib
import xml.dom.minidom

def createKML(self, cr, uid, data, context):
    # This function creates an XML document and adds the necessary
    # KML elements.
    address = ' '
    path = tools.config['addons_path']
    fileName = path + '/mymap.kml'
    
    cr.execute('select min(id) as id, sum(credit) as turnover, partner_id as partner_id from account_move_line group by partner_id')
    for id, turnover, partner_id in cr.fetchall():
        partner_obj = pooler.get_pool(cr.dbname).get('res.partner')
        partner = partner_obj.read(cr, uid, partner_id, ['name'])
        
    address_obj= pooler.get_pool(cr.dbname).get('res.partner.address')
#    address_ids = address_obj.search(cr, uid, ['partner_id', '=', partner_id])
    add = address_obj.browse(cr,uid,data['id'],context)
    
    if add.street:
        address += str(m.street)
    if add.street2:
        address += ', '
        address += str(m.street2)
    if add.city:
        address += ', '
        address += str(m.city)
    if add.state_id:
        address += ', '
        address += str(m.state_id.name)
    if add.country_id:
        address += ', '
        address += str(m.country_id.name)
    if add.zip:
        address += ' '
        address += str(m.zip)
    
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2','kml')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)
    placemarkElement = kmlDoc.createElement('Placemark')
    descriptionElement = kmlDoc.createElement('description')
    descriptionText = kmlDoc.createTextNode(address)
    descriptionElement.appendChild(descriptionText)
    placemarkElement.appendChild(descriptionElement)
    pointElement = kmlDoc.createElement('Point')
    placemarkElement.appendChild(pointElement)
    coorElement = kmlDoc.createElement('coordinates')
    
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
    
    # This geocodes the address and adds it to a <Point> element.
    coordinates = geocode(address)
    coorElement.appendChild(kmlDoc.createTextNode(coordinates))
    pointElement.appendChild(coorElement)
    documentElement.appendChild(placemarkElement)

    # This writes the KML Document to a file.
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toprettyxml(' '))  
    kmlFile.close()


class customer_on_map(wizard.interface):

    states= {'init' : {'actions': [],
                       'result':{'type':'action', 'action': createKML, 'state':'end'}
                       }
             }
customer_on_map('wizard_customer_on_map')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

