# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Gábor Dukai
#    Parts of this module are based on product_listprice_upgrade
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
    "name":"Product price update",
    "version":"1.05",
    "author":"Gábor Dukai",
    "website" : "http://exploringopenerp.blogspot.com",
    "category":"Generic Modules/Inventory Control",
    "description": """
    You can think of this module as product_listprice_upgrade v2.

    The aim of this module is to allow the automatic update of the price fields of products.
    * added a new pricelist type called 'Internal Pricelist' (currently, we have only 2 pricelist types: Sale and Purchase Pricelist)
    * Created a wizard button in the menu Products>Pricelist called 'Update Product Prices'
    * After filling in the wizard form and clicking on 'Update', it will change the selected price field of all products in the categories that we were selected in the wizard.

    Compatibility: tested with OpenERP v5.0
    """,
    "depends":["product"],
    "demo_xml":[],
    "update_xml":[
        'security/ir.model.access.csv',
        'pricelist_view.xml',
        'pricelist_data.xml'],
    "license": "GPL-3",
    "active":False,
    "installable":True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

