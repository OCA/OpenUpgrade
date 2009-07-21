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
import xml.dom.minidom
import base64

import wizard
import pooler

_earth_form =  '''<?xml version="1.0"?>
<form string="Google Map/Earth" >
    <field name="path" colspan="4"/>
    <newline/>
    <field name="refresh_mode" />
    <field name="refresh_interval" />
    <field name="view_refresh_mode" />
    <field name="view_refresh_time" />
    <newline/>
    <separator string="Select option to make kml" colspan="4"/>
    <field name="partner_select" />
    <field name="country_select" />
    <field name="route_select"  />
</form>'''

_earth_fields = {
    'path': {'string': 'Path (Etiny)', 'type': 'char', 'readonly': False , 'required': True, 'size':64, 'help':'etiny url'},
    'partner_select': {'string':'Partner', 'type': 'boolean', 'help':'KML with All Details of partners'},
    'country_select': {'string':'Country', 'type': 'boolean', 'help':'KML with All Details of partners and its country'},
    'route_select': {'string':'Delivery route', 'type': 'boolean', 'help':'Delivery route kml'},
    'refresh_mode':{
        'string':"RefreshMode",
        'type':'selection',
        'selection':[('onChange','onChange'),('onInterval','onInterval'),('onExpire','onExpire')],
        'default': lambda *a:'onInterval',
        'help': 'Specifies a time-based refresh mode'
    },
    'refresh_interval': {'string':'Refresh Interval', 'type': 'integer', 'default': lambda *a: 1, 'help':'Indicates to refresh the file every n seconds'},
    'view_refresh_mode':{
        'string':"ViewRefreshMode",
        'type':'selection',
        'selection':[('never','never'),('onStop','onStop'),('onRequest','onRequest'),('onRegion','onRegion')],
        'default': lambda *a:'onStop',
        'help': 'Specifies how the link is refreshed when the "camera" changes'
    },
    'view_refresh_time': {'string':'View Refresh Time', 'type': 'integer', 'default': lambda *a: 1, 'help': 'After camera movement stops, specifies the number of seconds to wait before refreshing the view'},
    }

_kml_form =  '''<?xml version="1.0"?>
<form string="Google Map/Earth">
    <separator string="Select path to store KML file" colspan="2"/>
    <newline/>
    <field name="name"/>
    <newline/>
    <field name="kml_file"/>
</form>'''

_kml_fields = {
        'name': {'string': 'KML File name', 'type': 'char', 'readonly': False , 'required': True},
        'kml_file': {'string': 'Save KML file', 'type': 'binary', 'required': True},
            }


def _create_kml(self, cr, uid, data, context={}):
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://maps.google.com/kml/2.2','kml')
    kmlElement.setAttribute('xmlns','http://www.opengis.net/kml/2.2')
    kmlDoc.appendChild(kmlElement)
    folderElement = kmlDoc.createElement('Folder')

    foldernameElement = kmlDoc.createElement('name')
    foldernameElement.appendChild(kmlDoc.createTextNode('Network Link Folder'))
    foldervisibilityElement = kmlDoc.createElement('visibility')
    foldervisibilityElement.appendChild(kmlDoc.createTextNode('0'))
    folderopenElement = kmlDoc.createElement('open')
    folderopenElement.appendChild(kmlDoc.createTextNode('0'))
    folderdescriptionElement = kmlDoc.createElement('description')
    folderdescriptionElement.appendChild(kmlDoc.createTextNode('Network Link'))
    folderNetworkLinkElement = kmlDoc.createElement('NetworkLink')

    folderElement.appendChild(foldernameElement)
    folderElement.appendChild(foldervisibilityElement)
    folderElement.appendChild(folderopenElement)
    folderElement.appendChild(folderdescriptionElement)
    folderElement.appendChild(folderNetworkLinkElement)
    folderElement.appendChild(foldernameElement)

    networknameElement = kmlDoc.createElement('name')
    networknameElement.appendChild(kmlDoc.createTextNode('Dynamic data'))
    networkvisibilityElement = kmlDoc.createElement('visibility')
    networkvisibilityElement.appendChild(kmlDoc.createTextNode('0'))
    networkopenElement = kmlDoc.createElement('open')
    networkopenElement.appendChild(kmlDoc.createTextNode('0'))
    networkdescriptionElement = kmlDoc.createElement('description')
    networkdescriptionElement.appendChild(kmlDoc.createTextNode('Network link'))
    networkrefreshVisibilityElement = kmlDoc.createElement('refreshVisibility')
    networkrefreshVisibilityElement.appendChild(kmlDoc.createTextNode('0'))
    networkflyToViewElement = kmlDoc.createElement('flyToView')
    networkflyToViewElement.appendChild(kmlDoc.createTextNode('0'))
    networkLinkElement = kmlDoc.createElement('Link')

    folderNetworkLinkElement.appendChild(networknameElement)
    folderNetworkLinkElement.appendChild(networkvisibilityElement)
    folderNetworkLinkElement.appendChild(networkopenElement)
    folderNetworkLinkElement.appendChild(networkdescriptionElement)
    folderNetworkLinkElement.appendChild(networkrefreshVisibilityElement)
    folderNetworkLinkElement.appendChild(networkflyToViewElement)
    folderNetworkLinkElement.appendChild(networkLinkElement)

    linkhrefElement = kmlDoc.createElement('href')
    linkhrefElement.appendChild(kmlDoc.createTextNode(data['form']['path']))
    linkrefreshModeElement = kmlDoc.createElement('refreshMode')
    linkrefreshModeElement.appendChild(kmlDoc.createTextNode(data['form']['refresh_mode']))
    linkrefreshIntervalElement = kmlDoc.createElement('refreshInterval')
    linkrefreshIntervalElement.appendChild(kmlDoc.createTextNode(str(data['form']['refresh_interval'])))
    linkviewRefreshModeElement = kmlDoc.createElement('viewRefreshMode')
    linkviewRefreshModeElement.appendChild(kmlDoc.createTextNode(data['form']['view_refresh_mode']))
    linkrefreshVisibilityElement = kmlDoc.createElement('refreshVisibility')
    linkrefreshVisibilityElement.appendChild(kmlDoc.createTextNode(str(data['form']['view_refresh_time'])))

    networkLinkElement.appendChild(linkhrefElement)
    networkLinkElement.appendChild(linkrefreshModeElement)
    networkLinkElement.appendChild(linkrefreshIntervalElement)
    networkLinkElement.appendChild(linkviewRefreshModeElement)
    networkLinkElement.appendChild(networkrefreshVisibilityElement)
    networkLinkElement.appendChild(linkrefreshVisibilityElement)

    kmlElement.appendChild(folderElement)
#    out = kmlDoc.toprettyxml(encoding='UTF-8')
    out = base64.encodestring(kmlDoc.toxml().encode('ascii', 'replace'))
    fname = 'mykml' + '.kml'
    return {'kml_file': out, 'name': fname}
#<Folder>
#<name>Network Links</name>
#    <visibility>0</visibility>
#    <open>0</open>
#    <description>Network link example 1</description>
#    <NetworkLink>
#      <name>Random Placemark</name>
#      <visibility>0</visibility>
#      <open>0</open>
#      <description>A simple server-side script that generates a new random placemark on each call</description>
#      <refreshVisibility>0</refreshVisibility>
#      <flyToView>0</flyToView>
#      <Link>
#        <href>http://jabber.openerp.co.in:8080/kml/?model=res.partner&amp;mode=1</href>
#        <refreshMode>onInterval</refreshMode>
#        <refreshInterval>2</refreshInterval>
#        <viewRefreshMode>onStop</viewRefreshMode>
#        <viewRefreshTime>7</viewRefreshTime>
#      </Link>
#    </NetworkLink>
#  </Folder>

class google_network_kml(wizard.interface):
    states = {
       'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_earth_form, 'fields':_earth_fields,  'state':[('end', 'Cancel'), ('make','Generate KML')]}
                },
       'make': {
            'actions': [_create_kml],
            'result': {'type': 'form', 'arch':_kml_form, 'fields':_kml_fields,  'state':[('end','Ok')]}
                },
            }
google_network_kml('google.network.link')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: