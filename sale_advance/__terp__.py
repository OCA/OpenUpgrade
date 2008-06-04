{
    "name" : "Sales: Sale Advance",
    "version" : "0.1",
    "author" : "Tiny",
    "category" : "Generic Modules/Sale Advance",
    "website" : "http://tinyerp.com/",
    "description": """
        * this module define wizard on sale.order ,for advance payment
            - create invoice from wizard""",
    "depends" : ["sale"],
    "init_xml" : [],
    "demo_xml" : ["sale_advance_demo.xml"],
    "update_xml" : ["sale_advance_wizard.xml"],
    "active": False,
    "installable": True
}
