{
	"name" : "Partial Payment on Invoices",
	"version" : "0.1",
	"depends" : ["account"],
	"author" : "Tiny",
	"description": """Prodide a new tab on invoices with partial payments.
Uses the partial reconciliation (>=4.3.0) system.
	""",
	"website" : "http://tinyerp.com/",
	"category" : "Generic Modules/Accounting",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		"invoice_view.xml",
	],

	"active": False,
	"installable": True
}
