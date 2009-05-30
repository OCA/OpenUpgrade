{
    "name" : "olap_sale",
    "version" : "0.1",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "depends" : ["olap"],
    "category" : "Generic Modules/Olap",
    "description": """
    Sale module will load the data in olap tables
    """,
    "init_xml" :  ['olap_data.xml'],
    "update_xml" :[],
    "demo_xml" : ['olap_sale.xml'],
    "active": False,
    "installable": True
}
