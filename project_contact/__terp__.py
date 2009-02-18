# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2008-2009 Syleam Info Services (<http://www.syleam.fr>). All Rights Reserved
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
    "name" : "Project Contact Management",
    "version": "1.0",
    "author" : "Syleam",
    "website" : "http://www.syleam.com",
    "category" : "Generic Modules/Projects & Services",
    "depends" : ["base", "base_contact", "project"],
    "description": """Module to managed contact on project when base_contact module is installed.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml": [
        "project_view.xml",
    ],
    'installable': True,
    'active': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
