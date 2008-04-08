{
	"name" : "Bookstore Verticalisation",
	"version" : "1.0",
	"author" : "Tiny",
	"category" : "Data Module",
	"depends" : ["library","delivery"],
	"init_xml" : ["partner_sequence.xml","bookstore_data.xml"],
	"update_xml": ["bookstore_view.xml","lot_sequence.xml",
				   "bookstore_report.xml","bookstore_access.xml",
				],
  	"demo_xml" : [],
	"installable": True,
}
