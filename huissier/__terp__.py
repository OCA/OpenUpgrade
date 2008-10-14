# -*- encoding: utf-8 -*-
{
    "name" : "Tiny ERP Huissiers",
    "author": "Tiny",
    "version" : "1.0",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/Others",
    "description": """Module for 'Maison de Vente des Huissiers de Justice'""",
    "depends" : ["base", "account"],
    "update_xml" : ["huissier_report.xml", "huissier_wizard.xml", "huissier_view.xml","huissier_invoice_view.xml"],
    "init_xml" : ["huissier_data.xml", "huissier_demo.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

