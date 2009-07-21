# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import os, xml, string, sys
from xml.dom.minidom import parse, parseString # remove me
import urllib
import base64
from lxml import etree

from osv import fields, osv
import tools

def _to_unicode(self, s):
    try:
        return s.encode('ascii')
    except UnicodeError:
        try:
            return s.decode('utf-8')
        except UnicodeError:
            try:
                return s.decode('latin')
            except UnicodeError:
                return s

def geocode(self, address):
        # This function queries the Google Maps API geocoder with an
        # address. It gets back a csv file, which it then parses and
        # returns a string with the longitude and latitude of the address.

        # This isn't an actual maps key, you'll have to get one yourself.
        # Sign up for one here: http://code.google.com/apis/maps/signup.html
        mapsKey = 'abcdefgh'
        mapsUrl = 'http://maps.google.com/maps/geo?q='

        # This joins the parts of the URL together into one string.
        url = ''.join([mapsUrl,urllib.quote(address.encode('utf-8')),'&output=csv&key=',mapsKey])

        # This retrieves the URL from Google.
        coordinates = urllib.urlopen(url).read().split(',')

        # This parses out the longitude and latitude, and then combines them into a string.
        coorText = '%s,%s' % (coordinates[3],coordinates[2])
        return coorText

def get_directions(self, source, destination):
    steps = []
    res = False
#    try:
    from google.directions import GoogleDirections
    gd = GoogleDirections('ABQIAAAAUbF6J26EmcC_0QgBXb9xvhRoz3DfI4MsQy-vo3oSCnT9jW1JqxQfs5OWnaBY9or_pyEGfvnnRcWEhA')
    res = gd.query(source, destination)
#    except:
#        raise wizard.except_wizard('Warning!','Please install Google direction package from http://pypi.python.org/pypi/google.directions/0.3 ')

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

class stock_move(osv.osv):
    _inherit = "stock.move"
    _description = "Stock Move"

    def get_kml(self, cr, uid, mode=0, context={}):

        colors = ['ff000080','ff800000','ff800080','ff808000','ff8080ff','ff80ff80','ffff8080','ffFACE87','ff1E69D','ff87B8DE', 'ff000000']
        warehouse_obj = self.pool.get('stock.warehouse')
        # fix me: sale_id is not null..we must have to create sale order!
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

#        XHTML_NAMESPACE = "http://maps.google.com/kml/2.2"
#        XHTML = "{%s}" % XHTML_NAMESPACE
#        NSMAP = {None : XHTML_NAMESPACE}
#        kml_root = etree.Element(XHTML + "kml", nsmap=NSMAP)
        kml_root = etree.Element("kml")

        kml_doc = etree.SubElement(kml_root, 'Document')
        etree.SubElement(kml_doc, 'name').text = 'Route'
        etree.SubElement(kml_doc, 'description').text = \
        ' Color  :           Number of Delivery range \n' \
        '=================================================================================================\n' \
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
        '=================================================================================================\n' \
        'Note: map display delivery route from warehouse location to customer locations(cities), it calculates number of deliveries by cities \n' \

        kml_poly = etree.SubElement(kml_doc, 'PolyStyle')
        etree.SubElement(kml_poly, 'fill').text = '1'
        etree.SubElement(kml_poly, 'outline').text = '1'

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

            kml_placemark = etree.SubElement(kml_doc, 'Placemark')
            etree.SubElement(kml_placemark, 'name').text = str(warehouse_city)
            etree.SubElement(kml_placemark, 'description').text = desc_text

            kml_style = etree.SubElement(kml_placemark, 'Style')
            kml_linestyle = etree.SubElement(kml_style, 'LineStyle')


            if pack['number_delivery'] >= no_of_packs_min and pack['number_delivery'] <= c1:
                etree.SubElement(kml_linestyle, 'color').text = colors[0]
            elif pack['number_delivery'] > c1 and pack['number_delivery'] <= c2:
                etree.SubElement(kml_linestyle, 'color').text = colors[1]
            elif pack['number_delivery'] > c2 and pack['number_delivery'] <= c3:
                etree.SubElement(kml_linestyle, 'color').text = colors[2]
            elif pack['number_delivery'] > c3 and pack['number_delivery'] <= c4:
                etree.SubElement(kml_linestyle, 'color').text = colors[3]
            elif pack['number_delivery'] > c4 and pack['number_delivery'] <= c5:
                etree.SubElement(kml_linestyle, 'color').text = colors[4]
            elif pack['number_delivery'] > c5 and pack['number_delivery'] <= c6:
                etree.SubElement(kml_linestyle, 'color').text = colors[5]
            elif pack['number_delivery'] > c6 and pack['number_delivery'] <= c7:
                etree.SubElement(kml_linestyle, 'color').text = colors[6]
            elif pack['number_delivery'] > c7 and pack['number_delivery'] <= c8:
                etree.SubElement(kml_linestyle, 'color').text = colors[7]
            elif pack['number_delivery'] > c8 and pack['number_delivery'] <= c9:
                etree.SubElement(kml_linestyle, 'color').text = colors[8]
            else:
                etree.SubElement(kml_linestyle, 'color').text = colors[9]

            etree.SubElement(kml_linestyle, 'width').text = '4'
            kml_linestring = etree.SubElement(kml_placemark, 'LineString')
            steps = get_directions(self, warehouse_city, customer_city)
            if not steps: # make route path strait
                coordinates1 = geocode(self, warehouse_city)
                coordinates2 = geocode(self, customer_city)
                coordinates2 = coordinates2 + '\n'
                etree.SubElement(kml_linestring, 'coordinates').text = coordinates2 + coordinates1
            else:
                for s in steps:
                    coorText = '%s, %s, %s \n' % (s[0], s[1], s[2])
                    etree.SubElement(kml_linestring, 'coordinates').text = coorText

        out = etree.tostring(kml_root, encoding="UTF-8", xml_declaration=True, pretty_print = False)
        return out
stock_move()

class res_country(osv.osv):
    _inherit = 'res.country'
    _description = 'Country'

    def get_kml(self, cr, uid, mode=0, context={}):
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
        colors = ['9f8080ff', '9f0000ff']
        partner_obj = self.pool.get('res.partner')
        address_obj= self.pool.get('res.partner.address')
        partner_ids = partner_obj.search(cr, uid, [])
        partners = partner_obj.browse(cr, uid, partner_ids)

        for part in partners:
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
        cr.execute("select sum(l.debit-l.credit), c.name from account_move_line l, res_country c, res_partner_address a, account_account act where l.partner_id = a.partner_id and c.id=a.country_id and l.account_id = act.id and act.type = 'receivable' group by c.name")
        res_partner = cr.fetchall()
        list_to = []
        for part in res_partner:
            if part[1]:
                res[string.upper(part[1])] = part[0]
                list_to.append(part[0])

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
        cr.execute("select min(aml.id) as id, sum(aml.debit - aml.credit) as turnover, aml.partner_id as partner_id from account_move_line aml, account_account ac, account_account_type actype where aml.account_id = ac.id and ac.user_type = actype.id and (ac.type = 'receivable') group by aml.partner_id")
        res_partner = cr.fetchall()
        for part in partners:
            res[part.id]= 0
        for ml_id, turnover, partner_id in res_partner:
            res[partner_id] = turnover
        ad = tools.config['addons_path'] # check for base module path also
        module_path = os.path.join(ad, 'google_earth/test.kml')
        dom1 = parse(module_path) # parse an XML file by name #use etree parse...(to do)
        placemarks = dom1.getElementsByTagName('Placemark')
        dict_country = {}

        for place in placemarks:
            name = place.getElementsByTagName('name')
            value_name = " ".join(t.nodeValue for t in name[0].childNodes if t.nodeType == t.TEXT_NODE)
            cord = place.getElementsByTagName('coordinates')
            value_cord = " ".join(t.nodeValue for t in cord[0].childNodes if t.nodeType == t.TEXT_NODE)

            if value_name in country_list:
                dict_country[value_name] = value_cord

        XHTML_NAMESPACE = "http://www.opengis.net/kml/2.2"
        XHTML = "{%s}" % XHTML_NAMESPACE
        NSMAP = {None : XHTML_NAMESPACE}
        kml_root = etree.Element(XHTML + "kml", nsmap=NSMAP)

        kml_doc = etree.SubElement(kml_root, 'Document')
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
                    address += tools.ustr(add.city)
                if add.state_id:
                    address += ', '
                    address += tools.ustr(add.state_id.name)
                if add.country_id:
                    address += ', '
                    address += tools.ustr(add.country_id.name)
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
            desc_text = '<html><head> <font size=1.9 color="red"> <b><table width=400 border=5 bordercolor="red"><tr><td> Partner Name</td><td>' + _to_unicode(self, part.name) + '</td></tr><tr>' + '<td> Partner Code</td><td> ' + str(part.ref or '') + '</td></tr>' + '<tr><td>Type:</td><td>' + type + '</td></tr><tr><td>' + 'Partner Address</td><td>' \
                        + _to_unicode(self, address) + '</td></tr>' + '<tr><td>Turnover of partner:</td><td> ' + str(res[part.id]) + '</td></tr>' + ' <tr><td> Main comapny</td><td>' + str(part.parent_id and part.parent_id.name) + '</td></tr>' + '<tr><td>Credit Limit</td><td>' + str(part.credit_limit or '') + '</td></tr>' \
                        + '<tr><td>Number of customer invoice</td><td>' + str(number_customer or 0 ) + '</td><tr>' +' <tr><td>Number of supplier invoice</td><td>' + str(number_supplier or 0) + '</td></tr>'  + '<tr><td>' +'Total Receivable</td><td> ' + str(part.credit) + '</td></tr>' +' <tr><td>Total Payable</td><td>' \
                        + str(part.debit or '') + '</td></tr>' + '<tr><td>Website</td><td>' + str(part.website or '') + '</td></tr>'+ '</table> </b> </font> </head></html>'

            kml_placemark = etree.SubElement(kml_doc, 'Placemark')
            etree.SubElement(kml_placemark, 'name').text = part.name
            etree.SubElement(kml_placemark, 'description').text = desc_text
            kml_point = etree.SubElement(kml_placemark, 'Point')

            # This geocodes the address and adds it to a <Point> element.
            coordinates = geocode(self, address)
            etree.SubElement(kml_point, 'coordinates').text = coordinates

        etree.SubElement(kml_doc, 'name').text = 'Country Wise Turnover'
        etree.SubElement(kml_doc, 'description').text = '============================= \n Light Red - Low Turnover \n Dart Red - High Turnover \n ============================='

        kml_folder = etree.SubElement(kml_doc, 'Folder')
        etree.SubElement(kml_folder, 'name').text = 'Folder'
        country_list.sort()
        for country in country_list:
            if res[country] > avg_to:
                color = colors[1]
            else:
                color = colors[0]
            cooridinate = dict_country[country]

            desctiption_country = '<html><head><font size=1.5 color="red"><b><table width=250 border=5 bordercolor="red"><tr><td>   Number of partner </td><td>' + str(res_cus[country])  +  line1 + '</td></tr><tr><td> Number of Invoices made </td><td>' + str(res_inv[country]) + line1 + \
                                  '</td></tr><tr><td>Turnover of country</td><td> ' + str(res[country]) +  line1 +' </td></tr></b> </font> </table></head></html>'
            kml_placemark1 = etree.SubElement(kml_folder, 'Placemark')
            etree.SubElement(kml_placemark1, 'name').text = country
            etree.SubElement(kml_placemark1, 'description').text = desctiption_country

            kml_style = etree.SubElement(kml_placemark1, 'Style')
            kml_polystyle = etree.SubElement(kml_style, 'PolyStyle')
            etree.SubElement(kml_polystyle, 'color').text = color

            kml_mgeometry = etree.SubElement(kml_placemark1, 'MultiGeometry')
            kml_polygon = etree.SubElement(kml_mgeometry, 'Polygon')

            kml_outerboundry = etree.SubElement(kml_polygon, 'outerBoundaryIs')
            kml_linearring = etree.SubElement(kml_outerboundry, 'LinearRing')

            etree.SubElement(kml_linearring, 'coordinates').text = cooridinate
#        out = kmlDoc.toxml(encoding='UTF-8')
        out = etree.tostring(kml_root, encoding="UTF-8", xml_declaration=True, pretty_print = False)
        return out

res_country()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _description = 'Partner'

    def get_kml(self, cr, uid, mode=0, context={}):
        partner_obj = self.pool.get('res.partner')
    #    path = tools.config['addons_path']
    #    fileName = path + '/google_earth/kml/partner.kml'
        partner_ids = partner_obj.search(cr, uid, [])
        partner_data = partner_obj.browse(cr, uid, partner_ids, context)
        address_obj= self.pool.get('res.partner.address')

        res = {}
        number_customer_inv=0
        number_supplier_inv=0
        cr.execute(''' select count(i.id),i.type, i.partner_id from account_invoice as i left join res_partner_address as a on i.partner_id=a.partner_id where i.type in ('out_invoice','in_invoice') group by i.type, i.partner_id ''')
        invoice_partner = cr.fetchall()

        cr.execute("select min(aml.id) as id, sum(aml.debit - aml.credit) as turnover, aml.partner_id as partner_id from account_move_line aml, account_account ac, account_account_type actype where aml.account_id = ac.id and ac.user_type = actype.id and (ac.type = 'receivable') group by aml.partner_id")
        res_partner = cr.fetchall()
        for part in partner_data:
            res[part.id]= 0
        for ml_id, turnover, partner_id in res_partner:
            res[partner_id] = turnover

        XHTML_NAMESPACE = "http://www.opengis.net/kml/2.2"
        XHTML = "{%s}" % XHTML_NAMESPACE
        NSMAP = {None : XHTML_NAMESPACE}
        kml_root = etree.Element(XHTML + "kml", nsmap=NSMAP)
#        kml_root = etree.Element("kml")

        kml_doc = etree.SubElement(kml_root, 'Document')
        etree.SubElement(kml_doc, 'name').text = 'partners'
        etree.SubElement(kml_doc, 'description').text = 'You can see Partner Information (Name, Code, Type, Partner Address, Turnover Partner, ....., Website) by clicking Partner'

        line = '<font color="blue">--------------------------------------------</font>'
        cnt_id = 0
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
    #            if add.street:
    #                address += '  '
    #                address += str(add.street)
    #            if add.street2:
    #                address += '  '
    #                address += str(add.street2)
                if add.city:
                    address += '  '
                    address += tools.ustr(add.city)
                if add.state_id:
                    address += ',  '
                    address += tools.ustr(add.state_id.name)
                if add.country_id:
                    address += ',  '
                    address += tools.ustr(add.country_id.name)
            kml_style = etree.SubElement(kml_doc, 'Style')
            kml_style.set('id','randomColorIcon'+ str(cnt_id+1))
            cnt_id += 1
            kml_iconstyle = etree.SubElement(kml_style, 'IconStyle')
            etree.SubElement(kml_iconstyle, 'color').text = 'ff00ff00'
            etree.SubElement(kml_iconstyle, 'colorMode').text = 'random'
            etree.SubElement(kml_iconstyle, 'scale').text = '1.1'
            kml_icon = etree.SubElement(kml_iconstyle, 'Icon')
            etree.SubElement(kml_icon, 'href').text = 'http://maps.google.com/mapfiles/kml/pal3/icon53.png'
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

            desc_text = '<html><head> <font size=1.5 color="red"> <b><table width=400 border=5 bordercolor="red"><tr><td> Partner Name</td><td>' + _to_unicode(self,part.name) + '</td></tr><tr>' + '<td> Partner Code</td><td> ' + str(part.ref or '') + '</td></tr>' + '<tr><td>Type</td><td>' + type + '</td></tr><tr><td>' + 'Partner Address</td><td>' \
                        + _to_unicode(self, address) + '</td></tr>' + '<tr><td>Turnover of partner</td><td> ' + str(res[part.id]) + '</td></tr>' + ' <tr><td> Main comapny</td><td>' + str(part.parent_id and part.parent_id.name) + '</td></tr>' + '<tr><td>Credit Limit</td><td>' + str(part.credit_limit or '') + '</td></tr>' \
                        + '<tr><td>Number of customer invoice</td><td>' + str(number_customer_inv or 0 ) + '</td><tr>' +' <tr><td>Number of supplier invoice</td><td>' + str(number_supplier_inv or 0) + '</td></tr>'  + '<tr><td>' +'Total Receivable</td><td> ' + str(part.credit or '') + '</td></tr>' +' <tr><td>Total Payable</td><td>' \
                        + str(part.debit or '') + '</td></tr>' + '<tr><td>Website</td><td>' + str(part.website or '') + '</td></tr>'+ '</table> </b> </font> </head></html>'

            kml_placemark = etree.SubElement(kml_doc, 'Placemark')
            etree.SubElement(kml_placemark, 'name').text = part.name
            etree.SubElement(kml_placemark, 'description').text = desc_text
            etree.SubElement(kml_placemark, 'styleUrl').text = 'root://styleMaps#default+nicon=0x304+hicon=0x314'
            # This geocodes the address and adds it to a <Point> element.
            coordinates = geocode(self, address)
            kml_point = etree.SubElement(kml_placemark, 'Point')
            etree.SubElement(kml_point, 'coordinates').text = coordinates
            # This writes the KML Document to a file.
        out = etree.tostring(kml_root, encoding="UTF-8", xml_declaration=True, pretty_print = False)
        return out

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
