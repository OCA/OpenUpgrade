{
	"name" : "Approve PO automatically when confirmed.",
	"version" : "1.0",
	"author" : "Tiny",
	"category" : "Generic Modules/Sales & Purchases",
	"description": """Automatically approve purchase orders when they are confirmed.""",
	"depends" : ["purchase"],
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["purchase_approve_workflow.xml"],
	"active": False,
	"installable": True,
}
