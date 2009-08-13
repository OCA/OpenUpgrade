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
{
    "name" : "Network Management Extension",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Enterprise Specific Modules/Information Technology",
    "website": "http://www.zikzakmedia.com",
    "depends" : ["network"],
    'init_xml': ['network_protocol_data.xml'],
    "demo_xml" : [],
    "update_xml" : [
        'security/ir.model.access.csv',
        "network_view.xml",
    ],
    "description": """
    Organize your software and configurations.
    - Additional network information: IP, domain, DNS, gateway
    - Protocols
    - Services
    - Ports
    - Public and private URLs
    """,
    "active" : False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

