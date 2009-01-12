# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2008 Smile.fr. All Rights Reserved
#    author: Raphaël Valyi
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
    "name":"Automates direct delivery between a supplier and a customer",
    "version":"0.9",
    "author":"Smile.fr for Loyalty Expert",
    "category":"Custom",
    "description": """
Enable to send goods directly form supplier to customer taking special care of:
- making only one picking from supplier location to customer location and using that picking in the sale_order workflow
- copying the sale order shipping address to the generate purchase order line (so merging purchase orders later on will still work)

Also take note of the following points:
1) We set automatically a Sale Order line to direct delivery if there isn't enough product in the stock.
2) We don't try to split such a line, but we set it entirely to direct delivery even if some products are available
3) In a sale order, some lines can be set to direct while some others are on stock at the same time
4) When we look if there is enough product on virtual stock for a line, we look at the time the sale order is confirmed,
we don't try to anticipate if there will be enough virtual stock is the future if the sale order is planned for later.
    """,
    "depends":["base", "product", "sale", "purchase"],
    "demo_xml":[],
    "update_xml":["product_view.xml", "sale_view.xml", "purchase_view.xml", "stock_view.xml", "supplier_export_data.xml"],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

