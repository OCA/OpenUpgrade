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
    coordinates = urllib.urlopen(url).read().split(',')

    # This parses out the longitude and latitude, and then combines them into a string.
    coorText = '%s,%s' % (coordinates[3],coordinates[2])
    return coorText

def create_kml(self, cr, uid, data, context={}):
    #Todo:
    #    check for all countries working with google or not (India..)
    #    icons
    # This function creates an XML document and adds the necessary
    # KML elements.
    res = {}
    res_inv = {}
    res_cus = {}
    address = ' '
    coordinates = []
    addresslist = []
    country_list = []
    coordinates_text = ' '
    number_customer=0
    number_supplier=0
    #colors = ['dfbf9f3b','88336699','59009900','880fff00','88f000cc','7fffffff','aaffffff','880fff00','880f00cc','88f000cc','33333333']
    colors = ['9f8080ff', '9f0000ff']
    pool = pooler.get_pool(cr.dbname)
    partner_obj = pool.get('res.partner')
    address_obj= pool.get('res.partner.address')
#    path = tools.config['addons_path']
#    fileName = path + '/google_earth/kml/partner_region.kml'
    partner_ids = partner_obj.search(cr, uid, [])
    partners = partner_obj.browse(cr, uid, partner_ids)

    for part in partners:
        #Todo: should be check for contact/defualt type address
        if part.address and part.address[0].country_id and part.address[0].country_id.name:
            if not string.upper(part.address[0].country_id.name) in country_list:
                cntry = string.upper(str(part.address[0].country_id.name))
                country_name = ''
                for char in cntry:
                    if char == '&':
                        country_name += 'AND'
                    else:
                        country_name += char
                country_list.append(country_name)
    map(lambda x:res.setdefault(x, 0.0), country_list)
    # fetch turnover by country (should be corect)
#    cr.execute('select sum(l.credit), c.name from account_move_line as l join res_partner_address as a on l.partner_id=a.partner_id left join res_country as c on c.id=a.country_id group by c.name')
    cr.execute("select sum(l.debit-l.credit), c.name from account_move_line l, res_country c, res_partner_address a, account_account act where l.partner_id = a.partner_id and c.id=a.country_id and l.account_id = act.id and act.type = 'receivable' group by c.name")
    res_partner = cr.fetchall()
    list_to = []
    for part in res_partner:
        if part[1]:
            res[string.upper(part[1])] = part[0]
            list_to.append(part[0])

#    avg_to = min(list_to) + max(list_to) / 2 or 0.0
    avg_to = list_to and (sum(list_to) / len(list_to)) or 0

    map(lambda x:res_inv.setdefault(x, 0), country_list)
    # fetch invoice by country
    cr.execute(''' select count(i.id),c.name from account_invoice as i left join res_partner_address as a on i.partner_id=a.partner_id left join res_country as c on a.country_id=c.id where i.type in ('out_invoice','in_invoice') group by c.name ''')
    invoice_partner = cr.fetchall()
    for part in invoice_partner:
        if part[1]:
            res_inv[str(string.upper(part[1]))] = str(part[0])

    # fetch number of costomer by country
    map(lambda x: res_cus.setdefault(x, 0), country_list)
    cr.execute(''' select count(distinct(p.id)), c.name, count(a.id) from res_partner as p left join res_partner_address as a on p.id=a.partner_id left join res_country as c on c.id=a.country_id group by a.country_id, c.name  ''')
    cust_country = cr.fetchall()

    for part in cust_country:
        if part[1]:
            res_cus[str(string.upper(part[1]))] = str(part[0])

    # fetch turnover by individual partner
#    cr.execute('select min(id) as id, sum(credit) as turnover, partner_id as partner_id from account_move_line group by partner_id')
    cr.execute("select min(aml.id) as id, sum(aml.debit - aml.credit) as turnover, aml.partner_id as partner_id from account_move_line aml, account_account ac, account_account_type actype where aml.account_id = ac.id and ac.user_type = actype.id and (ac.type = 'receivable') group by aml.partner_id")
    res_partner = cr.fetchall()
    for part in partners:
        res[part.id]= 0
    for ml_id, turnover, partner_id in res_partner:
        res[partner_id] = turnover
#    for part in partners:
#        for id, turnover, partner_id in res_partner:
#            if not (partner_id == part.id):
#                res[part.id] = 0
#            if partner_id == part.id:
#                res[part.id] = turnover

    ad = tools.config['addons_path'] # check for base module path also
    module_path = os.path.join(ad, 'google_earth/test.kml')
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
#    line = '<font color="blue">--------------------------------------------</font>'
    line1 = '<font color="blue"><br />--------------------------------------------</font>'
    line1 = ''
    for part in partners:
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
#            if add.street:
#                address += str(add.street)
#            if add.street2:
#                address += ', '
#                address += str(add.street2)
            if add.city:
                address += ''
                address += str(add.city)
            if add.state_id:
                address += ', '
                address += str(add.state_id.name)
            if add.country_id:
                address += ', '
                address += str(add.country_id.name)
        type = ''
        if part.customer:
            type += 'Customer '
            number_customer += 1
        if part.supplier:
            type += 'Supplier'
            number_supplier += 1

        if address == ', S. Georgia & S. Sandwich Isls.': # to be check
            address = ', South Georgia and the South Sandwich Islands'
        elif address == ', Saint Kitts & Nevis Anguilla':
            address = ', Saint Kitts and Nevis'

#        desc_text = ' <html><head> <font color="red"> <b> Partner Name : ' + str(part.name) + '<br/>' + line +'<br /> Partner Code : ' + str(part.ref or '') + '<br/>' + line + ' <br />Type : ' + type + ' <br/>' +line+ '<br /> Partner Address: ' +  address + '<br/>' +line+ '<br /> Turnover of partner : ' + str(res[part.id]) + '<br/>' +line+ ' <br /> Main comapny : ' + str(part.parent_id and part.parent_id.name) + '<br/>' + line+  ' <br />Credit Limit : ' + str(part.credit_limit) + '<br/>' \
#                    + line +  ' <br /> Number of customer invoice : ' + str(number_customer or 0 ) + '<br/>' + line+' <br /> Number of supplier invoice : ' + str(number_supplier or 0)  + '<br/>' +line +'<br />Total Receivable : ' + str(part.credit) + '<br/>' + line+' <br/>Total Payable : ' + str(part.debit) + '<br/>' + line+ '<br/>Website : ' + str(part.website or '') + '<br/>' +line+ ' </b> </font> </head></html>'
        desc_text = '<html><head> <font size=1.9 color="red"> <b><table width=400 border=5 bordercolor="red"><tr><td> Partner Name</td><td>' + str(part.name) + '</td></tr><tr>' + '<td> Partner Code</td><td> ' + str(part.ref or '') + '</td></tr>' + '<tr><td>Type:</td><td>' + type + '</td></tr><tr><td>' + 'Partner Address</td><td>' \
                    + address + '</td></tr>' + '<tr><td>Turnover of partner:</td><td> ' + str(res[part.id]) + '</td></tr>' + ' <tr><td> Main comapny</td><td>' + str(part.parent_id and part.parent_id.name) + '</td></tr>' + '<tr><td>Credit Limit</td><td>' + str(part.credit_limit) + '</td></tr>' \
                    + '<tr><td>Number of customer invoice</td><td>' + str(number_customer or 0 ) + '</td><tr>' +' <tr><td>Number of supplier invoice</td><td>' + str(number_supplier or 0) + '</td></tr>'  + '<tr><td>' +'Total Receivable</td><td> ' + str(part.credit) + '</td></tr>' +' <tr><td>Total Payable</td><td>' \
                    + str(part.debit) + '</td></tr>' + '<tr><td>Website</td><td>' + str(part.website or '') + '</td></tr>'+ '</table> </b> </font> </head></html>'

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
    documentElementname.appendChild(kmlDoc.createTextNode('Country Wise Turnover'))
    documentElementdesc = kmlDoc.createElement('description')
    documentElementdesc.appendChild(kmlDoc.createTextNode('============================= \n Light Red - Low Turnover \n Dart Red - High Turnover \n ============================='))

    documentElement.appendChild(documentElementname)
    documentElement.appendChild(documentElementdesc)

    folderElement = kmlDoc.createElement('Folder')
    foldernameElement = kmlDoc.createElement('name')
    foldernameElement.appendChild(kmlDoc.createTextNode('Folder'))
    folderElement.appendChild(foldernameElement)

    country_list.sort()
    for country in country_list:
        if res[country] > avg_to:
            color = colors[1]
        else:
            color = colors[0]
        cooridinate = dict_country[country]

#        desctiption_country = '<html><head> <font color="red"> <b> Number of partner: ' + str(res_cus[country])  +  line1 + '<br /> Number of Invoices made: ' + str(res_inv[country]) + line1 + '<br /> Turnover of country: ' + str(res[country]) +  line1 +' </b> </font> </head></html>'
        desctiption_country = '<html><head><font size=1.5 color="red"><b><table width=250 border=5 bordercolor="red"><tr><td>   Number of partner </td><td>' + str(res_cus[country])  +  line1 + '</td></tr><tr><td> Number of Invoices made </td><td>' + str(res_inv[country]) + line1 + \
                              '</td></tr><tr><td>Turnover of country</td><td> ' + str(res[country]) +  line1 +' </td></tr></b> </font> </table></head></html>'
        placemarkElement = kmlDoc.createElement('Placemark')
        placemarknameElement = kmlDoc.createElement('name')
        placemarknameText = kmlDoc.createTextNode(country)
        placemarkdescElement = kmlDoc.createElement('description')
        placemarkdescElement.appendChild(kmlDoc.createTextNode(desctiption_country))
        placemarknameElement.appendChild(placemarknameText)

        placemarkstyleElement = kmlDoc.createElement('Style')
        placemarkpolystyleElement = kmlDoc.createElement('PolyStyle')
        placemarkcolorrElement = kmlDoc.createElement('color')
        placemarkcolorrElement.appendChild(kmlDoc.createTextNode(color))#colors[cnt]
        placemarkpolystyleElement.appendChild(placemarkcolorrElement)
        placemarkstyleElement.appendChild(placemarkpolystyleElement)

        placemarkElement.appendChild(placemarknameElement)
        placemarkElement.appendChild(placemarkdescElement)
        placemarkElement.appendChild(placemarkstyleElement)

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

    out = base64.encodestring(kmlDoc.toxml())
    fname = 'region' + '.kml'
    return {'kml_file': out, 'name': fname}

class customer_on_map(wizard.interface):
    states = {
         'init': {
            'actions': [create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                }
            }
customer_on_map('layers.region.catery')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: