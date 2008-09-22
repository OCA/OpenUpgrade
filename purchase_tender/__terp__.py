# -*- encoding: utf-8 -*-
{
    "name" : "Purchase - Purchase Tender",
    "version" : "0.1",
    "author" : "Tiny",
    "category" : "Generic Modules/Purchase",
    "website" : "http://tinyerp.com/",
    "description": """ This module allows you to manage your Purchase Tenders. When a purchase order is created, you now have the opportunity to save the related tender. 
    This new object will regroup and will allow you to easily keep track and order all your purchase orders.
""",
    "depends" : ["purchase"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["purchase_tender_view.xml","purchase_tender_sequence.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

