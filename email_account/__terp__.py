# -*- encoding: utf-8 -*-
{
    "name" : "Email Invoice",
    "version" : "1.0",
    "depends" : ["smtpclient","account"],
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "description": """Use Email client module to send to customers or suppliers
the selected invoices attached by Email.

  * The sale order, invoice and shipping emails addresses are proposed
  * An email subject and text with the user signature are proposed
  * Later, the emails addresses, subject and text can be modified
  * A partner event is created with information of the email (partner,
    description, channel, document, user)
  * Historical and statistical data is recorded in the smtpclient module
""",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["account_invoice_wizard.xml"],
    "active": False,
    "installable": True
}
