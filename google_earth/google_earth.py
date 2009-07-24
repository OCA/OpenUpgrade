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
import urllib
from lxml import etree
import base64

from google.directions import GoogleDirections

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
    gd = GoogleDirections('ABQIAAAAUbF6J26EmcC_0QgBXb9xvhRoz3DfI4MsQy-vo3oSCnT9jW1JqxQfs5OWnaBY9or_pyEGfvnnRcWEhA')
    res = gd.query(source, destination)
#    except:
#        raise osv.except_osv('Warning!','Please install Google direction package from http://pypi.python.org/pypi/google.directions/0.3 ')
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

class google_map(osv.osv):
    _name = 'google.map'
    _description = 'Google Map/Earth'

    def get_kml(self, cr, uid, context={}):
        #fix me for path
        data = {'view_refresh_time': 1, 'refresh_mode': 'onInterval',
                'view_refresh_mode': 'onStop', 'path': 'http://yourserver.com:port/kml/',
                'models': ['res.country', 'res.partner', 'stock.move'], 'refresh_interval': 1}
        return self.get_networklink_kml(cr, uid, data=data, context=context)

    def add_network_link(self, cr, uid, url, data, context):
        folderNetworkLinkElement = etree.Element('NetworkLink')
        networknameElement = etree.Element('name')
        networknameElement.text = 'Dynamic data'
        networkvisibilityElement = etree.Element('visibility')
        networkvisibilityElement.text = '0'
        networkopenElement = etree.Element('open')
        networkopenElement.text = '0'
        networkdescriptionElement = etree.Element('description')
        networkdescriptionElement.text = 'Network link'
        networkrefreshVisibilityElement = etree.Element('refreshVisibility')
        networkrefreshVisibilityElement.text = '0'
        networkflyToViewElement = etree.Element('flyToView')
        networkflyToViewElement.text = '0'
        networkLinkElement = etree.Element('Link')

        folderNetworkLinkElement.append(networknameElement)
        folderNetworkLinkElement.append(networkvisibilityElement)
        folderNetworkLinkElement.append(networkopenElement)
        folderNetworkLinkElement.append(networkdescriptionElement)
        folderNetworkLinkElement.append(networkrefreshVisibilityElement)
        folderNetworkLinkElement.append(networkflyToViewElement)
        folderNetworkLinkElement.append(networkLinkElement)

        linkhrefElement = etree.Element('href')
        linkhrefElement.text = url
        linkrefreshModeElement = etree.Element('refreshMode')
        linkrefreshModeElement.text = data['refresh_mode']
        linkrefreshIntervalElement = etree.Element('refreshInterval')
        linkrefreshIntervalElement.text = str(data['refresh_interval'])
        linkviewRefreshModeElement = etree.Element('viewRefreshMode')
        linkviewRefreshModeElement.text = data['view_refresh_mode']
        linkrefreshVisibilityElement = etree.Element('refreshVisibility')
        linkrefreshVisibilityElement.text = str(data['view_refresh_time'])

        networkLinkElement.append(linkhrefElement)
        networkLinkElement.append(linkrefreshModeElement)
        networkLinkElement.append(linkrefreshIntervalElement)
        networkLinkElement.append(linkviewRefreshModeElement)
        networkLinkElement.append(networkrefreshVisibilityElement)
        networkLinkElement.append(linkrefreshVisibilityElement)
        return folderNetworkLinkElement

    def get_networklink_kml(self, cr, uid, data, context):
        '''
        data = {'view_refresh_time': 1, 'refresh_mode': 'onInterval',
                'view_refresh_mode': 'onStop', 'path': 'http://yourserver.com:port/kml/',
                'models': ['res.country', 'res.partner'], 'refresh_interval': 1}
        '''
        kmlElement = etree.Element("kml")
        kmlElement.set('xmlns',"http://www.opengis.net/kml/2.2")
        folderElement = etree.Element('Folder')

        foldernameElement = etree.Element('name')
        foldernameElement.text = 'Network Link Folder'
        foldervisibilityElement = etree.Element('visibility')
        foldervisibilityElement.text = '0'
        folderopenElement = etree.Element('open')
        folderopenElement.text = '0'
        folderdescriptionElement = etree.Element('description')
        folderdescriptionElement.text = 'Network Link'

        for model in data['models']:
            url = data['path'] + '?model=%s'% (model,)
            network_link = self.add_network_link(cr, uid, url, data, context)
            folderElement.append(network_link)

        folderElement.append(foldernameElement)
        folderElement.append(foldervisibilityElement)
        folderElement.append(folderopenElement)
        folderElement.append(folderdescriptionElement)
        #folderElement.append(folderNetworkLinkElement)
        folderElement.append(foldernameElement)
        kmlElement.append(folderElement)
        return etree.tostring(kmlElement, encoding="UTF-8", xml_declaration=True, pretty_print = True)

    def get_country_boundries(self, cr, uid, country_list, context):
        '''
        This function return boundries (coordinates) of all countries specified in
        country list by reading test.kml
        '''

        ad = tools.config['addons_path']
        module_path = os.path.join(ad, 'google_earth/test.kml')
        dict_country = {}
        doc = etree.parse(module_path)
        root = doc.getroot()
        placemarks = root.getchildren()[0].findall('{http://earth.google.com/kml/2.0}Placemark')

        for place in placemarks:
            name = place.findall('{http://earth.google.com/kml/2.0}name')
            if name:
                value_name = name[0].text
            cord = place.findall('{http://earth.google.com/kml/2.0}coordinates')
            for i in place.getchildren():
                x = i.findall('{http://earth.google.com/kml/2.0}outerBoundaryIs')
                if x:
                    y = x[0].findall('{http://earth.google.com/kml/2.0}LinearRing')
                    if y:
                        z = y[0].findall('{http://earth.google.com/kml/2.0}coordinates')
                        value_cord = z[0].text
                        if value_name in country_list:
                            dict_country[value_name] = value_cord
        return dict_country

    def get_placemark_kml(self, cr, uid, parent_element, datas, datas_country, context):
        '''
        parent_element = [name, description]
        datas = [{'name': 'partnername', 'address': 'Address of partner' 'desc': {'desc1': 'value1', 'desc2': 'value2', 'desc3': 'value3', .......}}
                ,{'name': 'partnername', 'address': 'Address of partner' 'desc': {'desc1': 'value1', 'desc2': 'value2', 'desc3': 'value3', .......}},
                .......]
        datas_country = [{'name': 'countryname', 'cooridinate': 'boundries of country cooridinate' 'desc': {'desc1': 'value1', 'desc2': 'value2', 'desc3': 'value3', .......}}
                ,{'name': 'countryname', 'cooridinate': 'boundries of country cooridinate' 'desc': {'desc1': 'value1', 'desc2': 'value2', 'desc3': 'value3', .......}},
        '''
        XHTML_NAMESPACE = "http://www.opengis.net/kml/2.2"
        XHTML = "{%s}" % XHTML_NAMESPACE
        NSMAP = {None : XHTML_NAMESPACE}
        kml_root = etree.Element(XHTML + "kml", nsmap=NSMAP)
        kml_doc = etree.SubElement(kml_root, 'Document')
        etree.SubElement(kml_doc, 'name').text = parent_element[0]
        etree.SubElement(kml_doc, 'description').text = parent_element[1]
        geocode_dict = {}
        for data in datas:
            desc_text = '<html><head><font color="red" size=1.9><b> <table border=5 bordercolor="blue">'
            html_text = ''
            for d in data['desc']:
                html_text += '<tr><td>' + d + '</td><td>' + data['desc'][d] + '</td></tr>'
            desc_text += html_text + '</table></b>  </font></head></html>'

            kml_placemark = etree.SubElement(kml_doc, 'Placemark')
            etree.SubElement(kml_placemark, 'name').text = data['name']
            etree.SubElement(kml_placemark, 'description').text = desc_text
            kml_point = etree.SubElement(kml_placemark, 'Point')
            # This geocodes the address and adds it to a <Point> element.
            if data['address'] in geocode_dict:
                coordinates = geocode_dict[data['address']]
            else:
                coordinates = geocode(self, data['address'])
                geocode_dict[data['address']] = coordinates
            etree.SubElement(kml_point, 'coordinates').text = coordinates
        kml_folder = etree.SubElement(kml_doc, 'Folder')
        etree.SubElement(kml_folder, 'name').text = 'Folder'

        for data in datas_country:
            desc_text = '<html><head><font color="red" size=1.9><b> <table border=5 bordercolor="blue">'
            html_text = ''
            for d in data['desc']:
                html_text += '<tr><td>' + d + '</td><td>' + data['desc'][d] + '</td></tr>'
            desc_text += html_text + '</table></b>  </font></head></html>'

            kml_placemark1 = etree.SubElement(kml_folder, 'Placemark')
            etree.SubElement(kml_placemark1, 'name').text = data['name']
            etree.SubElement(kml_placemark1, 'description').text = desc_text
            kml_style = etree.SubElement(kml_placemark1, 'Style')
            kml_polystyle = etree.SubElement(kml_style, 'PolyStyle')
            etree.SubElement(kml_polystyle, 'color').text = data['color']
            kml_mgeometry = etree.SubElement(kml_placemark1, 'MultiGeometry')
            kml_polygon = etree.SubElement(kml_mgeometry, 'Polygon')
            kml_outerboundry = etree.SubElement(kml_polygon, 'outerBoundaryIs')
            kml_linearring = etree.SubElement(kml_outerboundry, 'LinearRing')
            etree.SubElement(kml_linearring, 'coordinates').text = data['cooridinate']

        return etree.tostring(kml_root, encoding="UTF-8", xml_declaration=True, pretty_print = False)

    def get_direction_kml(self, cr, uid, parent_element, datas, context):
        '''
        parent_element = [name, description]
        datas = [{'color': 'ff000080', 'source_city': 'Belgium', 'destination_city': 'Berlin', 'desc': {'desc1': 'value1', 'desc2': 'value2', 'desc3': 'value3', .......}}
                ,{'color': 'ff000080', 'source_city': 'Belgium', 'destination_city': 'Berlin', 'desc': {'desc1': 'value1', 'desc2': 'value2', 'desc3': 'value3', .......}},
                .......]
        '''

        XHTML_NAMESPACE = "http://www.opengis.net/kml/2.2"
        XHTML = "{%s}" % XHTML_NAMESPACE
        NSMAP = {None : XHTML_NAMESPACE}
        kml_root = etree.Element(XHTML + "kml", nsmap=NSMAP)
        kml_doc = etree.SubElement(kml_root, 'Document')
        etree.SubElement(kml_doc, 'name').text = parent_element[0]
        etree.SubElement(kml_doc, 'description').text = parent_element[1]
        direction_dict = {}
        for data in datas:
            desc_text = '<html><head><font color="red" size=1.9><b> <table border=5 bordercolor="blue">'
            html_text = ''
            for d in data['desc']:
                html_text += '<tr><td>' + d + '</td><td>' + data['desc'][d] + '</td></tr>'
            desc_text += html_text + '</table></b>  </font></head></html>'

            kml_placemark = etree.SubElement(kml_doc, 'Placemark')
            etree.SubElement(kml_placemark, 'name').text = data['destination_city']
            etree.SubElement(kml_placemark, 'description').text = desc_text
            kml_style = etree.SubElement(kml_placemark, 'Style')
            kml_linestyle = etree.SubElement(kml_style, 'LineStyle')
            etree.SubElement(kml_linestyle, 'color').text = data['color']
            etree.SubElement(kml_linestyle, 'width').text = '4'
            kml_linestring = etree.SubElement(kml_placemark, 'LineString')

            if data['source_city']+' '+data['destination_city'] in direction_dict:
                steps = direction_dict[data['source_city']+' '+data['destination_city']]
            else:
                steps = get_directions(self, data['source_city'], data['destination_city'])
                direction_dict[data['source_city']+' '+data['destination_city']] = steps
            if not steps: # make route path strait
                coordinates1 = geocode(self, data['source_city'])
                coordinates2 = geocode(self, data['destination_city'])
                coordinates2 = coordinates2 + '\n'
                etree.SubElement(kml_linestring, 'coordinates').text = coordinates2 + coordinates1
            else:
                for s in steps:
                    coorText = '%s, %s, %s \n' % (s[0], s[1], s[2])
                    etree.SubElement(kml_linestring, 'coordinates').text = coorText
        return etree.tostring(kml_root, encoding="UTF-8", xml_declaration=True, pretty_print=False)

google_map()

class stock_move(osv.osv):
    _inherit = "stock.move"
    _description = "Stock Move"

    def get_kml(self, cr, uid, context={}):
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

        parent_element = []
        text = \
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
        'Note: map display delivery route from warehouse location to customer locations(cities), it calculates number of deliveries by cities \n'

        parent_element.append('Route')
        parent_element.append(text)
        line = ''
        master_dict = {}
        child_dict = {}
        list_data = []
        for pack in packings:
            total_qty = pack['product_send']
            warehouse_city = warehouse_dict[pack['warehouse_id']]
            customer_city = pack['customer_city']
            customer_country = pack['customer_country']
            if not (warehouse_city and customer_city):
                raise osv.except_osv('Warning!','Address is not defiend on warehouse or customer. ')

            if pack['number_delivery'] >= no_of_packs_min and pack['number_delivery'] <= c1:
                child_dict['color'] = colors[0]
            elif pack['number_delivery'] > c1 and pack['number_delivery'] <= c2:
                child_dict['color'] = colors[1]
            elif pack['number_delivery'] > c2 and pack['number_delivery'] <= c3:
                child_dict['color'] = colors[2]
            elif pack['number_delivery'] > c3 and pack['number_delivery'] <= c4:
                child_dict['color'] = colors[3]
            elif pack['number_delivery'] > c4 and pack['number_delivery'] <= c5:
                child_dict['color'] = colors[4]
            elif pack['number_delivery'] > c5 and pack['number_delivery'] <= c6:
                child_dict['color'] = colors[5]
            elif pack['number_delivery'] > c6 and pack['number_delivery'] <= c7:
                child_dict['color'] = colors[6]
            elif pack['number_delivery'] > c7 and pack['number_delivery'] <= c8:
                child_dict['color'] = colors[7]
            elif pack['number_delivery'] > c8 and pack['number_delivery'] <= c9:
                child_dict['color'] = colors[8]
            else:
                child_dict['color'] = colors[9]
            child_dict['source_city'] = warehouse_city
            child_dict['destination_city'] = customer_city
            master_dict['desc'] = {'Warehouse location': warehouse_city, 'Customer Location': customer_city+' '+customer_country, \
                                   'Number of product sent': str(total_qty), 'Number of delivery': str(pack['number_delivery'])}

            child_dict['desc'] = master_dict['desc']
            list_data.append(child_dict)

        return self.pool.get('google.map').get_direction_kml(cr, uid, parent_element, list_data, context)#.encode('utf-8')

stock_move()

class res_country(osv.osv):
    _inherit = 'res.country'
    _description = 'Country'

    def get_kml(self, cr, uid, context={}):
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

        dict_country = self.pool.get('google.map').get_country_boundries(cr, uid, country_list, context)
        line1 = '<font color="blue"><br />--------------------------------------------</font>'
        line1 = ''
        list_data = []
        for part in partners:
            child_dict = {}
            master_dict = {}
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

            cntry_name = add.country_id.name
            if cntry_name and not cntry_name.find('&')== '-1':
                cntry_name = cntry_name.replace('&','and')
            if cntry_name == "Afghanistan, Islamic State of":
                cntry_name = 'Afghanistan'
            elif cntry_name == "Andorra, Principality of":
                cntry_name = 'Andorra'
            elif cntry_name == "Cambodia, Kingdom of":
                cntry_name = 'Cambodia'
            elif cntry_name == "Congo, The Democratic Republic of the":
                cntry_name = 'Congo'
            if add:
                if add.city:
                    address += ''
                    address += tools.ustr(add.city)
#                if add.state_id:
#                    address += ', '
#                    address += tools.ustr(add.state_id.name)
                if add.country_id:
                    address += ', '
                    address += tools.ustr(cntry_name)
            type = ''
            if part.customer:
                type += 'Customer '
                number_customer += 1
            if part.supplier:
                type += 'Supplier'
                number_supplier += 1

            # This geocodes the address and adds it to a <Point> element.
            child_dict['name'] = part.name
            master_dict['desc'] = {' Partner Name ': _to_unicode(self, part.name), ' Partner Code ': str(part.ref or '') , \
                                   ' Type: ': type, ' Partner Address ': _to_unicode(self, address), ' Turnover of partner: ':str(res[part.id]), \
                                   ' Main company ': str(part.parent_id and part.parent_id.name), ' Credit Limit ': str(part.credit_limit or ''), \
                                   ' Number of customer invoice ': str(number_customer or 0 ), ' Number of supplier invoice ': str(number_supplier or 0) ,\
                                   ' Total Receivable ': str(part.credit), ' Total Payable ': str(part.debit or ''), ' Website ': str(part.website or '')}
            child_dict['desc'] = master_dict['desc']
            child_dict['address'] = address
            list_data.append(child_dict)

        text = '============================= \n Light Red - Low Turnover \n Dart Red - High Turnover \n ============================='
        parent_element = []
        parent_element.append('Country Wise Turnover')
        parent_element.append(text)

        country_list.sort()
        list_data_cntry = []
        for country in country_list:
            master_dict_cntry = {}
            child_dict_cntry = {}
            if res[country] > avg_to:
                color = colors[1]
            else:
                color = colors[0]
            cooridinate = dict_country[country]
            child_dict_cntry['name'] = country
            master_dict_cntry['desc'] = {'Number of partner': str(res_cus[country]), 'Number of Invoices made': str(res_inv[country]), 'Turnover of country': str(res[country]) }
            child_dict_cntry['desc'] = master_dict_cntry['desc']
            child_dict_cntry['address'] = address
            child_dict_cntry['color'] = color
            child_dict_cntry['cooridinate'] = cooridinate
            list_data_cntry.append(child_dict_cntry)
        return self.pool.get('google.map').get_placemark_kml(cr, uid, parent_element, list_data, list_data_cntry, context)#.encode('utf-8')

res_country()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _description = 'Partner'

    def get_kml(self, cr, uid, context={}):
        partner_obj = self.pool.get('res.partner')
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

        line = '<font color="blue">--------------------------------------------</font>'
        parent_element = []
        parent_element.append('partners')
        parent_element.append('You can see Partner Information (Name, Code, Type, Partner Address, Turnover Partner, ....., Website) by clicking Partner')
        list_data = []
        for part in partner_data:
            child_dict = {}
            master_dict = {}
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
                if add.city:
                    address += '  '
                    address += tools.ustr(add.city)
#                if add.state_id:
#                    address += ',  '
#                    address += tools.ustr(add.state_id.name)
                if add.country_id:
                    address += ',  '
                    address += tools.ustr(add.country_id.name)
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

            # This geocodes the address and adds it to a <Point> element.
            child_dict['name'] = part.name
            master_dict['desc'] = {'Partner Name': _to_unicode(self, part.name), 'Partner Code': str(part.ref or '') , \
                                   'Type:': type, 'Partner Address': _to_unicode(self, address), 'Turnover of partner:':str(res[part.id]), \
                                   'Main company': str(part.parent_id and part.parent_id.name), 'Credit Limit': str(part.credit_limit or ''), \
                                   'Number of customer invoice': str(number_customer_inv or 0 ), 'Number of supplier invoice': str(number_supplier_inv or 0) ,\
                                   'Total Receivable': str(part.credit), 'Total Payable': str(part.debit or ''), 'Website': str(part.website or '')}
            child_dict['desc'] = master_dict['desc']
            child_dict['address'] = address
            list_data.append(child_dict)
            # This writes the KML Document to a file.
        return self.pool.get('google.map').get_placemark_kml(cr, uid, parent_element, list_data, [], context)#.encode('utf-8')

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: