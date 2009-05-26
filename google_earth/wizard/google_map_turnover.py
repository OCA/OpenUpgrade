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
#    try:
    coordinates = urllib.urlopen(url).read().split(',')
#    except:
#        raise wizard.except_wizard(_('Connection Error !'),_('Please check your internet connection'))

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
    number_customer_inv=0
    number_supplier_inv=0
#    cr.execute('select min(id) as id, sum(credit) as turnover, partner_id as partner_id from account_move_line group by partner_id')

    cr.execute(''' select count(i.id),i.type, i.partner_id from account_invoice as i left join res_partner_address as a on i.partner_id=a.partner_id where i.type in ('out_invoice','in_invoice') group by i.type, i.partner_id ''')
    invoice_partner = cr.fetchall()

    cr.execute("select min(aml.id) as id, sum(aml.credit) as turnover, aml.partner_id as partner_id from account_move_line aml, account_account ac, account_account_type actype where aml.account_id = ac.id and ac.user_type = actype.id and (ac.type = 'receivable') group by aml.partner_id")
    res_partner = cr.fetchall()
    for part in partner_data:
        res[part.id]= 0
    for ml_id, turnover, partner_id in res_partner:
        res[partner_id] = turnover

    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://maps.google.com/kml/2.2','kml')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    kmlElement.appendChild(documentElement)
    documentElementname = kmlDoc.createElement('name')
    documentElementname.appendChild(kmlDoc.createTextNode('partners'))
    documentElementdesc = kmlDoc.createElement('description')
    documentElementdesc.appendChild(kmlDoc.createTextNode('You can see Partner information by clicking Partner'))
    documentElement.appendChild(documentElementname)
    documentElement.appendChild(documentElementdesc)
    line = '<font color="blue">--------------------------------------------</font>'
    for part in partner_data:
        partner_id = part.id
        address = ''
        mul_address = partner_obj.address_get(cr, uid, [part.id], adr_pref=['default', 'contact', 'invoice', 'delivery'])
        address_all = map(lambda x: x and x[1], mul_address.items())
        par_address_id = mul_address.get('contact', False)
        if not par_address_id:
            par_address_id = mul_address.get('default', False)
            if not par_address_id:
                par_address_id = address_all and address_all[0] or False
        if par_address_id:
            add = address_obj.browse(cr, uid, par_address_id, context)

        if add:
            address += ''
            if add.street:
                address += '  '
                address += str(add.street)
            if add.street2:
                address += '  '
                address += str(add.street2)
            if add.city:
                address += '  '
                address += str(add.city)
            if add.state_id:
                address += ',  '
                address += str(add.state_id.name)
            if add.country_id:
                address += ',  '
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
        hrefElement.appendChild(kmlDoc.createTextNode('http://maps.google.com/mapfiles/kml/pal3/icon53.png'))
        iconElement.appendChild(hrefElement)
        iconstyleElement.appendChild(iconElement)
        styleElement.appendChild(iconstyleElement)
        documentElement.appendChild(styleElement)
        type = ''
        if part.customer:
            type += 'Customer '
        if part.supplier:
            type += 'Supplier'

        for partner in invoice_partner:
            if partner[1] == 'out_invoice' and partner[2] == partner_id:
                number_customer_inv = partner[0]
            if partner[1] == 'in_invoice' and partner[2] == partner_id:
                number_supplier_inv = partner[0]


        desc_text = ' <html><head> <font color="red"> <b> Partner Name : ' + str(part.name) + '<br/>' + line +'<br /> Partner Code : ' + str(part.ref or '') + '<br/>' + line + ' <br />Type : ' + type + ' <br/>' +line+ '<br /> Partner Address: ' +  address + '<br/>' +line+ '<br /> Turnover of partner : ' + str(res[part.id]) + '<br/>' +line+ ' <br /> Main comapny : ' + str(part.parent_id and part.parent_id.name) + '<br/>' + line+  ' <br />Credit Limit : ' + str(part.credit_limit) + '<br/>' \
                    + line +  ' <br /> Number of customer invoice : ' + str(number_customer_inv or 0 ) + '<br/>' + line+' <br /> Number of supplier invoice : ' + str(number_supplier_inv or 0)  + '<br/>' +line +'<br />Total Receivable : ' + str(part.credit) + '<br/>' + line+' <br/>Total Payable : ' + str(part.debit) + '<br/>' + line+ '<br/>Website : ' + str(part.website or '') + '<br/>' +line+ ' </b> </font> </head></html>'
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
        styleurlElement.appendChild(kmlDoc.createTextNode('root://styleMaps#default+nicon=0x304+hicon=0x314'))
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

    out = base64.encodestring(kmlDoc.toxml())
    fname = 'turnover' + '.kml'
    return {'kml_file': out, 'name': fname}

class customer_on_map(wizard.interface):

    states = {
         'init': {
            'actions': [create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                }
            }

customer_on_map('google.earth')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: