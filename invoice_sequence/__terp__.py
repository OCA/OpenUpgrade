# -*- encoding: utf-8 -*-
{
    "name" : "Invoice lines with sequence number",
    "version" : "0.1",
    "depends" : ["account", "base"],
    "author" : "Tiny",
    "description": """Prodide a new field on the invoice line form, allowing to manage the lines order.
    """,
    "website" : "http://tinyerp.com/",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "invoice_view.xml",
    ],

    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

