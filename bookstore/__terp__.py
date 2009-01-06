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
    "name" : "Bookstore Verticalisation",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Others",
    "description": """Module to manage book store.
    Add book Information, 
    Author Information, 
    Books Category,
    Related books,
    Available Languages,
""",
    "depends" : ["library","delivery","sale"],
    "init_xml" : ["partner_sequence.xml","bookstore_data.xml"],
    "update_xml": ["bookstore_view.xml","lot_sequence.xml",
                   "bookstore_report.xml","bookstore_access.xml",
                ],
    "demo_xml" : ['book_data.xml'],
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

