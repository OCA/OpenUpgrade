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
    "name":"Visible Discount Module",
    "version":"1.0",
    "author":"Tiny",
    "category":"Generic Modules/Inventory Control",
    "description": """
    This module use for calculate discount amount on Sale order line and invoice line  base on partner's pricelist
    For that,On the pricelists form, new check box called "Visible Discount" is added.
    Example:
        For product PC1, listprice=450, for partner Asustek, his pricelist calculated is 225 for PC1
        If the check box is ticked, we will have on the SO line (and so also on invoice line): Unit price=450, Discount=50,00, Net price=225
        If the check box is NOT ticked, we will have on SO and Invoice lines: Unit price=225, Discount=0,00, Net price=225

    """,
    "depends":["base","product","account","sale"],
    "demo_xml":[],
    "update_xml":['product_view.xml'],
    "active":False,
    "installable":True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

