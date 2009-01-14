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
    "name":"WARNING: THIS IS STILL A WORK IN PROGRESS - Manage the maintenance contracts of a product fleet",
    "version":"0.2",
    "author":"Smile.fr for Anevia",
    "category":"Custom",
    "depends":["base", "product", "stock", "sale", "crm_configuration", "account", "delivery"],#the delivery dependence is important
    #because if delivery is installed, then declaring the dependence controls where our stock.picking.action_invoice_create action is called
    #and makes it properly add extra invoice line fields to the invoice line, even if invoiced on delivery. 
    "demo_xml":[],
    #"update_xml":[],
    "update_xml":["product_view.xml", "sale_view.xml", "invoice_view.xml", "stock_view.xml", "partner_view.xml", "account_view.xml", "crm_view.xml", "crm_sequence.xml"],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

