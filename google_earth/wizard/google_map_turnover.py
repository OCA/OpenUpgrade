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

import wizard
import pooler
import tools
import base64

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
    # This wizard will be remove in future because it wll be merge with layer wizard
    # This function creates an XML document and adds the necessary
    # KML elements.
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
#    path = tools.config['addons_path']
#    fileName = path + '/google_earth/kml/partner.kml'
    partner_ids = partner_obj.search(cr, uid, [])
    partner_data = partner_obj.browse(cr, uid, partner_ids, context)
    address_obj= pool.get('res.partner.address')

    res = {}
#    cr.execute('select min(id) as id, sum(credit) as turnover, partner_id as partner_id from account_move_line group by partner_id')
    cr.execute("select min(aml.id) as id, sum(aml.credit) as turnover, aml.partner_id as partner_id from account_move_line aml, account_account ac, account_account_type actype where aml.account_id = ac.id and ac.user_type = actype.id and (actype.name = 'income' or ac.type = 'receivable') group by aml.partner_id")
    res_partner = cr.fetchall()
    for part in partner_data:
        for id, turnover, partner_id in res_partner:
            if not (partner_id == part.id):
                res[part.id] = 0
            if partner_id == part.id:
                res[part.id] = turnover
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://maps.google.com/kml/2.2','kml')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    kmlElement.appendChild(documentElement)
    documentElementname = kmlDoc.createElement('name')
    documentElementname.appendChild(kmlDoc.createTextNode('Turnover by partners'))
    documentElement.appendChild(documentElementname)
#    kmlFile = open(fileName, 'w')
    for part in partner_data:
        address = ''
        add = address_obj.browse(cr, uid, part.address and part.address[0].id, context) # Todo: should be work for multiple address
        if add:
        #    if add.street:
        #        address += str(add.street)
        #    if add.street2:
        #        address += ', '
        #        address += str(add.street2)
            if add.city:
        #        address += ', '
                address += str(add.city)
            if add.state_id:
                address += ', '
                address += str(add.state_id.name)
            if add.country_id:
                address += ', '
                address += str(add.country_id.name)

        styleElement = kmlDoc.createElement('Style')
        styleElement.setAttribute('id','randomColorIcon')
        iconstyleElement = kmlDoc.createElement('IconStyle')
        colorElement = kmlDoc.createElement('color')
        colorElement.appendChild(kmlDoc.createTextNode('ff00ff00'))
        iconstyleElement.appendChild(colorElement)
        colormodeElement = kmlDoc.createElement('colorMode')
        colormodeElement.appendChild(kmlDoc.createTextNode('random'))
        iconstyleElement.appendChild(colormodeElement)
        scaleElement = kmlDoc.createElement('scale')
        scaleElement.appendChild(kmlDoc.createTextNode('1.1'))
        iconstyleElement.appendChild(scaleElement)
        iconElement = kmlDoc.createElement('Icon')
        hrefElement = kmlDoc.createElement('href')
        hrefElement.appendChild(kmlDoc.createTextNode('http://maps.google.com/mapfiles/kml/pal3/icon48.png'))
        iconElement.appendChild(hrefElement)
        iconstyleElement.appendChild(iconElement)
        styleElement.appendChild(iconstyleElement)
        documentElement.appendChild(styleElement)

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
        styleurlElement = kmlDoc.createElement('styleUrl')
        styleurlElement.appendChild(kmlDoc.createTextNode('#randomColorIcon'))
        placemarkElement.appendChild(styleurlElement)
        pointElement = kmlDoc.createElement('Point')
        placemarkElement.appendChild(pointElement)
        coorElement = kmlDoc.createElement('coordinates')
        # This geocodes the address and adds it to a <Point> element.
        coordinates = geocode(address)
        coorElement.appendChild(kmlDoc.createTextNode(coordinates))
        pointElement.appendChild(coorElement)
        documentElement.appendChild(placemarkElement)
        # This writes the KML Document to a file.


#    kmlFile.write(kmlDoc.toprettyxml(' '))
#    kmlFile.close()
    out = base64.encodestring(kmlDoc.toxml())
    fname = 'turnover' + '.kml'
    return {'kml_file': out, 'name': fname}

class customer_on_map(wizard.interface):

    states = {
         'init': {
            'actions': [create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Done')]}
                }
            }

customer_on_map('google.earth')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: