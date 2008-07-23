# -*- encoding: utf-8 -*-
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
    "website" : "http://tinyerp.com/",
    "category" : "Generic Modules/CRM & SRM",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "crm_livechat_view.xml","crm_demo_data.xml"
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

