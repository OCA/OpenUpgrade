import urllib
import xml.dom.minidom
from google.directions import GoogleDirections

import wizard
import pooler
import tools

_earth_form = '''<?xml version="1.0"?>
        <form string="Google Map/Earth">
        <label string="kml file created in ../google_earth/kml/route.kml , You can upload on google map online"/>
        </form> '''

_earth_fields = {}

def geocode(address):
    mapsKey = 'abcdefgh'
    mapsUrl = 'http://maps.google.com/maps/geo?q='
    url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',mapsKey])
    coordinates = urllib.urlopen(url).read().split(',')
    coorText = '%s,%s' % (coordinates[3],coordinates[2])
    return coorText

def get_directions(source,destination):
    steps=[]
    gd = GoogleDirections('ABQIAAAAUbF6J26EmcC_0QgBXb9xvhRoz3DfI4MsQy-vo3oSCnT9jW1JqxQfs5OWnaBY9or_pyEGfvnnRcWEhA')
    res = gd.query(source,destination)
    if res.status != 200:
        print "Address not found. Status was: %d" % res.status
        return False
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
    #    3. should be store at user's location not in specific path of /google_earth/kml/ , use binary field
    #    4. should be test for all cities (Shanghai -> Hongkong ) check to upper and lower possiblities to search

    #Note: from google.directions import GoogleDirections : this package shuld be install in order to run the wizard
    path = tools.config['addons_path']
    fileName = path + '/google_earth/kml/route.kml'

    # To find particular location
    pool = pooler.get_pool(cr.dbname)
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://maps.google.com/kml/2.2','kml')
    kmlElement = kmlDoc.appendChild(kmlElement)

    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)

    styleElement = kmlDoc.createElement('Style')
    styleElement.setAttribute('id','style15')

    linestyleElement = kmlDoc.createElement('LineStyle')
    colorElement = kmlDoc.createElement('color')
    colorElement.appendChild(kmlDoc.createTextNode('80000000'))
    linestyleElement.appendChild(colorElement)
    widthElement = kmlDoc.createElement('width')
    widthElement.appendChild(kmlDoc.createTextNode('3'))
    linestyleElement.appendChild(widthElement)
    styleElement.appendChild(linestyleElement)

    polystyleElement = kmlDoc.createElement('PolyStyle')
    polycolorElement = kmlDoc.createElement('color')
    polycolorElement.appendChild(kmlDoc.createTextNode('59009900'))
    polystyleElement.appendChild(polycolorElement)
    fillElement = kmlDoc.createElement('fill')
    fillElement.appendChild(kmlDoc.createTextNode('1'))
    polystyleElement.appendChild(fillElement)
    outlineElement = kmlDoc.createElement('outline')
    outlineElement.appendChild(kmlDoc.createTextNode('1'))
    polystyleElement.appendChild(outlineElement)
    documentElement.appendChild(polystyleElement)
    documentElement.appendChild(styleElement)

    for pack in pool.get('stock.picking').browse(cr, uid, data['ids']):
        if not pack.sale_id:
            #display some exception here
            continue
        warehouse_city = pack.sale_id.shop_id.warehouse_id.partner_address_id.city
        customer_city = pack.address_id.city

        placemarkElement = kmlDoc.createElement('Placemark')
        placemarknameElement = kmlDoc.createElement('name')
        placemarknameText = kmlDoc.createTextNode(warehouse_city)

        placemarknameElement.appendChild(placemarknameText)
        placemarkElement.appendChild(placemarknameElement)

        lineElement = kmlDoc.createElement('LineString')
        placemarkElement.appendChild(lineElement)

        coorElement = kmlDoc.createElement('coordinates')
        lineElement.appendChild(coorElement)

        steps = get_directions(warehouse_city, customer_city)
        if not steps: # make route path strait
            coordinates1 = geocode(warehouse_city)
            coorElement.appendChild(kmlDoc.createTextNode(coordinates1))
            coordinates2 = geocode(customer_city)
            coorElement.appendChild(kmlDoc.createTextNode(coordinates2))
        else:
            for s in steps:
                coorText = '%s,%s,%s' % (s[0], s[1], s[2])
                coorElement.appendChild(kmlDoc.createTextNode(coorText))

        lineElement.appendChild(coorElement)
        documentElement.appendChild(placemarkElement)

        # This writes the KML Document to a file.
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toprettyxml(' '))
    kmlFile.close()
    return {}

class find_route(wizard.interface):

    states = {
       'init': {
            'actions': [_create_kml],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end','Ok')]}
                },
            }
find_route('google.find.route')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: