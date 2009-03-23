{
	"name" : "OScommerce Interface / ZenCart",
	"version" : "1.0",
	"author" : "Axelor/Zikzakmedia",
	"category" : "Interface OScommerce",
	"website" : "http://www.zikzakmedia.com",
	"depends" : ["product", "stock", "sale"],
	"description": """OSCommerce (Zencart) eCommerce interface synchronisation.
Users can order on the website, orders are automatically imported in OpenERP.

You can export products, stock level and create links between
categories of products, taxes and languages.

If you product has an image attached, it sends the image to the OScommerce website.

Developed by Tiny, Axelor and Zikzakmedia""",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		"security/esale_oscom_security.xml",
		"security/ir.model.access.csv",
		"esale_oscom_view.xml",
		"esale_oscom_wizard.xml",
		"esale_oscom_product_view.xml",
		"shipping_product_data.xml"
	],
	"active": False,
	"installable": True
}
