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
    "name":"Help managing maintenance contracts related to product fleet",
    'description': """
Manage the maintenance contracts of a product fleet (streaming servers originally).

Now partners have fleets and sub-fleets for which they can buy products that can eventually
be covered by paid maintenance contracts.

Fleet: a stock.location for which all products have the same maintenance end date anniversary.
Indeed, it's useful to have several maintenance contracts for a given partner with a single anniversary date
for an eventual renewal.
Meaning that if the customer wants a different end date anniversaries for two mainteance contracts,
then he should have several Fleets.
Products don't go in the Fleets actually, they go in their Sub-Fleets instead.

Sub-Fleet: a stock.location child of a Fleet which might contains some purchased products.
In a sub-fleet, ALL the maintenance contracts of the products have exactly the same start date and end date.
Meaning that if a customer need several different start date or some years offset for the end date,
then he should have several Sub-Fleets.

This module also take care of proposing ideal maintenance dates given a few rules that might
be changed in your specific case (Ideally they wouldn't be hardcoded or at least have some
parameters externalized to the database).

Finally, this module also takes care of after sale incidents, extending the native CRM and thus
preserving all the CRM power.
Given a product serial number (prodlot), it's able to retrieve the Fleet and Partner and know if a product is still covered
by a maintenance contract or not. It also deals with reparation movements in a simple manner, that
might later on made compatible with the mrp_repair module which was too complex for our first use here. 

This module is also fully compliant with the native prodlot tracking of OpenERP to knwo
where is a serial number, be it a finished product or only a part, and even after a replacement
if movements are properly entered in the crm incident. For a better tracking experience, it's
advised to use it along with the mrp_prodlot_autosplit module. 
    """,
    "version":"0.3",
    "author":"Smile for Anevia (Anevia.com)",
    "website": "http://www.smile.fr",
    "category":"Custom",
    "depends":["base", "product", "stock", "sale", "crm_configuration", "account", "delivery"],#the delivery dependence is important
    #because if delivery is installed, then declaring the dependence controls where our stock.picking.action_invoice_create action is called
    #and makes it properly add extra invoice line fields to the invoice line, even if invoiced on delivery. 
    "demo_xml":["fleet_demo.xml"],
    #"update_xml":[],
    "update_xml":["product_view.xml", "sale_view.xml", "invoice_view.xml", "stock_view.xml", "partner_view.xml", "account_view.xml", "crm_view.xml", "crm_sequence.xml"],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

