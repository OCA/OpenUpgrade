# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2008 Raphaël Valyi
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
    "name" : "Stock Management",
    "version" : "0.9.0",
    "author" : "Raphaël Valyi",
    "website" : "http://rvalyi.blogspot.com",
    "depends" : ["product", "stock"],
    "category" : "Generic Modules/Inventory Control",
    "description":"""Turn production lot tracking codes into unique codes 
    associated per product instance. Moreover, it
    1) add a new checkbox on the product form to enable or disable this behavior
    2) then forbid to perform a move if a move involves more than one product instance
    3) automagically splits up picking list movements into one movement per product instance
    4) turn incoming pickings into an editable grid where you can directly type the code
    of a new production number/code to create and associate to the move (it also checks it
    doesn't exist yet)""",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["product_view.xml", "stock_view.xml"],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: