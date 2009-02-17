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
    "name" : "CRM - Livechat Jabber Client",
    "version" : "1.3",
    "depends" : ["base"],
    "author" : "Tiny",
    "description": """
This module allows you to configure and manage a livechat on your website.
So that your salesman can directly talk with your users in your website, using
their normal jabber account. This project includes two parts:
* An OpenERP module to manage everything
* A python Ajax client to set on your website for the end-user interface.

It allows you to define:
* XMPP (Jabber) Accounts for your users
* XMPP Accounts for anonymous customers

Then based one some events (a customer visiting some pages), it can open a
window so that the visitor can directly talk with your teams. It goes to a
jabber user according to what you configured in the OpenERP interface.
    """,
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/CRM & SRM",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "security/ir.model.access.csv",
        "crm_livechat_view.xml",
        "crm_demo_data.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

