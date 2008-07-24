# -*- encoding: utf-8 -*-
{
    "name" : "Carriers and deliveries For Purchase Order",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Sales & Purchases",
    "description": "Allows to add delivery methods in purchase order and packings. You can define your own carrier and delivery grids for prices. When creating invoices from pickings, Tiny ERP is able to add and compute the shipping line.",
    "depends" : ["sale","purchase", "stock",'delivery'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["delivery_view.xml","delivery_wizard.xml"],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

