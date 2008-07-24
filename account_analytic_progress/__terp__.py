# -*- encoding: utf-8 -*-
{
    "name" : "account_analytic_progress",
    "description": """Progress bar for analytic accounts.
This is the module used for displaying the shared funded
development projects on the Tiny ERP website.""",
    "version" : "1.0",
    "author" : "tiny",
    "category" : "Generic Modules/Accounting",
    "module": "",
    "website": "http://tinyerp.com",
    "depends" : ["account_analytic_analysis"],
    "init_xml" : [],
    "update_xml" : [
        "account_analytic_progress_view.xml"
    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

