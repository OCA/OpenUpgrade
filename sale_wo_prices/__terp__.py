# -*- encoding: utf-8 -*-
{
    "name" : "Sales without prices",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "category" : "Generic Modules/Sales & Purchases",
    "description": """Hides prices in sales and product forms. Only sale manager can see them. Normal salesmen can do sales without seeing the product prices.""",
    "depends" : ["sale", "product"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "product_view.xml",
        "sale_view.xml",
    ],
    "active": False,
    "installable": True
}
