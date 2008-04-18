{
    "name" : "ecommerce",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/ecommerce",
    "description": "Ecomemrce module",
    "depends" : ["base", "product","account","sale"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["configuration/configuration_view.xml","catalog/catalog_view.xml","partner/partner_new_view.xml","configuration/configuration_workflow.xml","configuration/sale_sequence.xml"],
    "active": False,
    "installable": True,
}
