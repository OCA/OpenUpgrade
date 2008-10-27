# -*- encoding: utf-8 -*-
{
    "name" : "Sales Forecast and Statistics",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "depends" : ["account", "account_invoice_salesman","crm"],
    "category" : "Generic Modules/Accounting",
    "description": """This module allows manager to do their sales forecast.
Different reports are set up for forecast and sales analysis.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "report_invoice_salesman_view.xml"
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

