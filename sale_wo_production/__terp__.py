{
	"name" : "Sales Without production",
	"version" : "0.1",
	"author" : "Tiny",
	"website" : "http://tinyerp.com/",
	"depends" : ["sale","mrp"],
	"category" : "Generic Modules/Sales & Purchases",
	"description": """Provide the scheduler wizard, the procurement and
the exception sub-menu from the mrp menu in the inventory control menu. This allow to hide easily the Mrp menu.""",
	"init_xml" : ["sale_wo_production_view.xml","sale_wo_production_wizard.xml"],
	"demo_xml" : [],
	"update_xml" : [],
	"active": False,
	"installable": True
}
