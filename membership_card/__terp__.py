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
  "name" : "Membership card",
  "version" : "1.0",
  "author" : "Zikzakmedia SL",
  "category" : "Generic Modules/Association",
  "website": "www.zikzakmedia.com",
  "license" : "GPL-3",
  "description": """Adds a photo field to partner contact.
Prints membership cards with name, number, bar code and photo of contacts.
  """,
  "depends" : ["base"],
  "init_xml" : [],
  "demo_xml" : [],
  "update_xml" : ["membership_card_view.xml","membership_card_report.xml",],
  "active": False,
  "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: