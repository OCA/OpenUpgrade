# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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
    "name" : "Partner labels",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "license" : "GPL-3",
    "category" : "Generic Modules",
    "description": """Flexible partner labels:
  * Definition of page sizes, label manufacturers and label formats
  * Flexible label formats (page size, portrait or landscape, manufacturer, rows, columns, width, height, top margin, left margin, ...)
  * Initial data for page sizes and label formats (from Avery and Apli manufacturers)
  * Wizard to print labels. The label format, the printer margins, the font type and size, the first label (row and column) to print on the first page can be set.""",
    "depends" : ["base",],
    "init_xml" : [
        "report_label_data.xml",
    ],
    "demo_xml" : [],
    "update_xml" : [
        "security/ir.model.access.csv",
        "partner_wizard.xml",
        "report_label_view.xml",
    ],
    "active": False,
    "installable": True
}
