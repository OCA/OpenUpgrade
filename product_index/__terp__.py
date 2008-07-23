#
# Use the custom module to put your specific code in a separate module.
#
{
    "name" : "Manage indexes on products prices",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Sales & Purchases",
    "website": "http://www.tinyerp.com",
    "depends" : ["product"],
    "demo_xml" : ['product.index.csv'],
    "init_xml" : [],
    "update_xml" : ['product_data.xml', "product_index_view.xml", "product_view.xml"],
    "active": False,
    "installable": True
}
