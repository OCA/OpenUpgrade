{
	"name" : "account_invoice_layout",
	"version" : "1.0",
	"depends" : ["base", "account"],
	"author" : "Tiny",
	"description": """
	This module provides some features to improve the layout of the invoices.

	It gives you the possibility to
		* order all the lines of an invoice
		* add titles, comment lines, sub total lines
		* draw horizontal lines and put page breaks
		* report to print invoices with given spcial message at the bottom of invoice


	""",
	"website" : "http://tinyerp.com/",
	"category" : "Generic Modules/Project & Services",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
					"account_invoice_layout_view.xml",
					"account_invoice_layout_report.xml",
					],
	"active": False,
	"installable": True
}
