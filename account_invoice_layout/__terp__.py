{
	"name" : "account_invoice_layout",
	"version" : "1.0",
	"depends" : ["base", "account"],
	"author" : "Tiny",
	"description": """
	This module provide some features to improve the layout of the invoices. 

	It gives you the possibility to 
		* order all the lines of an invoice
		* add titles, comment lines, sub total lines
		* draw horizontal lines and put page breaks
		

	""",
	"website" : "http://tinyerp.com/",
	"category" : "Generic Modules/Project & Services",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
					"account_invoice_layout_view.xml",
					],
	"active": False,
	"installable": True
}
