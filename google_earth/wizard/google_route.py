import urllib
import xml.dom.minidom
import base64

import wizard
import pooler
import tools
from osv import osv,fields

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
    mapsKey = 'abcdefgh'
    mapsUrl = 'http://maps.google.com/maps/geo?q='
    url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',mapsKey])
    coordinates = urllib.urlopen(url).read().split(',')
    coorText = '%s,%s' % (coordinates[3],coordinates[2])
    return coorText

def get_directions(source, destination):
    steps = []
    res = False
    try:
        from google.directions import GoogleDirections
        gd = GoogleDirections('ABQIAAAAUbF6J26EmcC_0QgBXb9xvhRoz3DfI4MsQy-vo3oSCnT9jW1JqxQfs5OWnaBY9or_pyEGfvnnRcWEhA')
        res = gd.query(source,destination)
    except:
        raise wizard.except_wizard('Warning!','Please install Google direction package from http://pypi.python.org/pypi/google.directions/0.3 ')

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

def _create_kml(self, cr, uid, data, context={}):
    #Todo:
    #    1. should be work with different country cities currenly it takes strait path if cities are in differnt countries
    #    2. you can put differnt data on path like product sent, etc
    #    3. should be test for all cities (Shanghai -> Hongkong ) check to upper and lower possiblities to search
    #    4. different colors accoridingly to number of deleveries

    #Note: from google.directions import GoogleDirections : this package shuld be install in order to run the wizard
#    path = tools.config['addons_path']
#    fileName = path + '/google_earth/kml/route.kml'
    colors = ['ff000080','ff800000','ff800080','ff808000','ff8080ff','ff80ff80','ffff8080','ff008000','ff008070','ff700070']

    # To find particular location
    pool = pooler.get_pool(cr.dbname)
    warehouse_obj = pool.get('stock.warehouse')
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://maps.google.com/kml/2.2','kml')
    kmlElement = kmlDoc.appendChild(kmlElement)

    documentElement = kmlDoc.createElement('Document')
    kmlElement.appendChild(documentElement)
    documentElementname = kmlDoc.createElement('name')
    documentElementname.appendChild(kmlDoc.createTextNode('Delivery route'))

#    styleElement = kmlDoc.createElement('Style')
#    styleElement.setAttribute('id','style15')
#
#    linestyleElement = kmlDoc.createElement('LineStyle')
#    colorElement = kmlDoc.createElement('color')
#    colorElement.appendChild(kmlDoc.createTextNode('80000000'))
#    linestyleElement.appendChild(colorElement)
#    widthElement = kmlDoc.createElement('width')
#    widthElement.appendChild(kmlDoc.createTextNode('3'))
#    linestyleElement.appendChild(widthElement)
#    styleElement.appendChild(linestyleElement)

    polystyleElement = kmlDoc.createElement('PolyStyle')
#    polycolorElement = kmlDoc.createElement('color')
#    polycolorElement.appendChild(kmlDoc.createTextNode('59009900'))
#    polystyleElement.appendChild(polycolorElement)
    fillElement = kmlDoc.createElement('fill')
    fillElement.appendChild(kmlDoc.createTextNode('1'))
    polystyleElement.appendChild(fillElement)
    outlineElement = kmlDoc.createElement('outline')
    outlineElement.appendChild(kmlDoc.createTextNode('1'))
    polystyleElement.appendChild(outlineElement)
    documentElement.appendChild(polystyleElement)
    documentElement.appendChild(documentElementname)

    cr.execute('select sp.warehouse_id, sum(m.product_qty) as product_send, count(s.id) as number_delivery,a.city as customer_city from stock_picking as s left join sale_order as so on s.sale_id=so.id left join sale_shop as sp on so.shop_id=sp.id left join stock_warehouse as w on w.id=sp.warehouse_id left join stock_move as m on s.id=m.picking_id left join res_partner_address as a on a.id=s.address_id  left join res_partner as p on p.id=a.partner_id where sale_id is not null group by a.city,sp.warehouse_id;')
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

#    value = no_of_packs_min + (no_of_packs_max - no_of_packs_min)/2 # 25 50 75 100
#    no_of_packs_min = no_of_packs_min + value/2
#    c1 = no_of_packs_min + value/2
#    c2 = c1 + value/2

    lower_limit = []
    interval = no_of_packs_max / 10
    lower_limit.append(no_of_packs_min)
    for j in range(no_of_packs_min, no_of_packs_max):
        lower_limit.append(no_of_packs_min + interval)
        no_of_packs_min += interval

    i=0
    for pack in packings:
        total_qty = pack['product_send']
        warehouse_city = warehouse_dict[pack['warehouse_id']]
        customer_city = pack['customer_city']
        if not (warehouse_city and customer_city):
            raise wizard.except_wizard('Warning!','Address is not defiend on warehouse or customer. ')

        desc_text = ' <html><head> <font color="red"> <b> [ Warehouse location : ' + warehouse_city + ' ]' + '  <br />[ Customer Location : ' + customer_city + ' ]' + ' <br />[ Number of product sent : ' + str(total_qty) + ' ]' + \
        ' <br />[ Number of delivery : ' + str(pack['number_delivery']) + ' ]' + '</b> </font> </head></html>'

        placemarkElement = kmlDoc.createElement('Placemark')
        placemarknameElement = kmlDoc.createElement('name')
        placemarknameText = kmlDoc.createTextNode(str(warehouse_city))
        placemarkdescElement = kmlDoc.createElement('description')
#        placemarkdescElement.appendChild(kmlDoc.createTextNode('Warehouse location: ' + warehouse_city + ',Customer Location: ' + customer_city + ',Planned Date: ' + plane_date + ' ,Sale order reference: ' + str(pack.origin or '') + ',Number of product sent: ' + str(total_qty)))
#        placemarkdescElement.appendChild(kmlDoc.createTextNode('Warehouse location: ' + warehouse_city + ',Customer Location: ' + customer_city + ',Number of product sent: ' + str(total_qty)))
        placemarkdescElement.appendChild(kmlDoc.createTextNode(desc_text))
        placemarknameElement.appendChild(placemarknameText)
        placemarkElement.appendChild(placemarknameElement)
        placemarkElement.appendChild(placemarkdescElement)

        styleElement = kmlDoc.createElement('Style')
        placemarkElement.appendChild(styleElement)
        linestyleElement = kmlDoc.createElement('LineStyle')
        styleElement.appendChild(linestyleElement)
        colorElement = kmlDoc.createElement('color')

#        if pack['number_delivery'] < no_of_packs_min:
#            colorElement.appendChild(kmlDoc.createTextNode(colors[0]))
#        elif pack['number_delivery'] > no_of_packs_min and pack['number_delivery'] < c1:
#            colorElement.appendChild(kmlDoc.createTextNode(colors[1]))
#        elif pack['number_delivery'] > c1 and pack['number_delivery'] < c2:
#            colorElement.appendChild(kmlDoc.createTextNode(colors[2]))
#        else:
#            colorElement.appendChild(kmlDoc.createTextNode(colors[3]))

        if len(lower_limit)==1:
            if pack['number_delivery'] > lower_limit[0]:
                colorElement.appendChild(kmlDoc.createTextNode(colors[i]))
        elif pack['number_delivery'] > lower_limit[i]:
                colorElement.appendChild(kmlDoc.createTextNode(colors[i]))
                i+=1
        else:
            colorElement.appendChild(kmlDoc.createTextNode(colors[0]))

        widthElement = kmlDoc.createElement('width')
        widthElement.appendChild(kmlDoc.createTextNode('4'))

        linestyleElement.appendChild(colorElement)
        linestyleElement.appendChild(widthElement)

        lineElement = kmlDoc.createElement('LineString')
        placemarkElement.appendChild(lineElement)

        coorElement = kmlDoc.createElement('coordinates')
        lineElement.appendChild(coorElement)

        steps = get_directions(warehouse_city, customer_city)
        if not steps: # make route path strait
            coordinates1 = geocode(warehouse_city)
            coordinates1 = coordinates1 + '\n'
            coorElement.appendChild(kmlDoc.createTextNode(coordinates1))
            coordinates2 = geocode(customer_city)
            coorElement.appendChild(kmlDoc.createTextNode(coordinates2))
        else:
            for s in steps:
                coorText = '%s, %s, %s \n' % (s[0], s[1], s[2])
                coorElement.appendChild(kmlDoc.createTextNode(coorText))

        lineElement.appendChild(coorElement)
        documentElement.appendChild(placemarkElement)
    out = base64.encodestring(kmlDoc.toxml())
    fname = 'route' + '.kml'
    return {'kml_file': out, 'name': fname}

class delivery_route(wizard.interface):

    states = {
       'init': {
            'actions': [_create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                },
            }
delivery_route('google.find.route')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: