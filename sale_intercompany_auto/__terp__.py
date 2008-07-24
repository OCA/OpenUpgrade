# -*- encoding: utf-8 -*-
{
    "name" : "Sale Inter-Company - Fully Automatic",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com/module_sale.html",
    "depends" : ["sale", "purchase"],
    "category" : "Generic Modules/Sales & Purchases",
    "description": """
    This module automatically generates inter-company documents, without
    confirmations or validation steps. When a purchase order is confirmed,
    if the partner exist in one of the company <> from the current one, it
    generates a SO.

    Company C1: Sale order -> Purchase Order (MTO)
    Inter-Co : Confirm Purchase Order (C1)
    Inter-Co : Purchase Order (C1) -> Sale Order (C2)
    Inter-Co : Confirm Sale Order (C2)
    Company C2: Continue... picking/porduction/C3

    It also works in cascade if you installed the mrp_jit module.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

