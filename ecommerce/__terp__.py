{
    "name" : "E-Commerce",
    "version" : "1.0",
    "author" : "e-tiny",
    "website" : "http://www.etiny.com",
    "depends" : ["base", "product","sale"],
    "category" : "Generic Modules/E-Commerce Shop",
    "init_xml" : [],
    "demo_xml" : ["ecommerce_demo_data.xml"],
    "description": """
    """,
    "update_xml" : [
                    "tools/ecom_product_view.xml",
                    "basic_info_view.xml",
                    "catalog/catalog_view.xml",
                    "tools/tools_wizard.xml",
                    "partner/partner_new_view.xml",
                    "sale_order/sale_order_view.xml",
                    "sale_order/saleorder_workflow.xml"
      
    ],
    "active": False,
    "installable": True
}
