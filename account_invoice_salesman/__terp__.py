# -*- encoding: utf-8 -*-
{
    "name" : "Salesman on invoices",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "depends" : ["account"],
    "category" : "Generic Modules/Accounting",
    "description": "This module adds a salesman on each invoice.",
    "init_xml" : [],
    "demo_xml" : [ ],
    "update_xml" : [
        "account_invoice_salesman_view.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

