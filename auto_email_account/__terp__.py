# -*- encoding: utf-8 -*-
{
    "name" : "Email Invoice",
    "version" : "1.0",
    "depends" : ["smtpclient","account"],
    "author" : "Tiny",
    "description": """Use Email client module to send to customers or suppliers
the selected invoices attached by Email
""",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "account_invoice_wizard.xml",
        "account_workflow.xml"
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

