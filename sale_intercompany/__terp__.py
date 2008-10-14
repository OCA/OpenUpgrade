# -*- encoding: utf-8 -*-
{
    "name" : "Sale Inter-Company",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com/module_sale.html",
    "depends" : ["sale", "crm", "product", "account"],
    "category" : "Generic Modules/Sales & Purchases",
    "description": """
    This module adds a shortcut on the purchase order to automaticalle
    create an assicated sale order.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["sale_interco_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

