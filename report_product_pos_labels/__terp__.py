# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2009 P. Christeas. All Rights Reserved
#
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 of the License.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "POS labels for product, lots",
    "version" : "0.1",
    "depends" : [ "base", "product", "stock", "point_of_sale_print" ],
    "author" : "P. Christeas",
    "description": """
      Sample labels for product, product lots. This module only contains
      these data, however has more dependencies than point_of_sale_print.
    """,
    "website" : "http://www.hellug.gr",
    "category" : "Generic Modules/Others",
    "init_xml" : [ 
    ],
    "demo_xml" : [
    ],
    "update_xml" : [ "report_postxt2.xml"
    ],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

