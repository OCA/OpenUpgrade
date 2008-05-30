{
	"name" : "CCI Translation",
	"version" : "1.0",
	"author" : "Tiny",
	"website" : "http://tinyerp.com",
	"category" : "Generic Modules/CCI Translation",
	"description": """
		cci translation
	""",
	"depends" : ["base","cci_mission","cci_account"],
	"init_xml" : [],
	"demo_xml" : ["cci_translation_data.xml"],

	"update_xml" : ["cci_translation_view.xml", "cci_translation_workflow.xml", "cci_translation_wizard.xml"],
	"active": False,
	"installable": True
}
