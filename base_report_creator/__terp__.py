{
	"name" : "Report Creator",
	"version" : "1.0",
	"author" : "Tiny",
	"website" : "",
	"category" : "Generic Modules/Base",
	"description": """This modules allows you to create any statistic
report on several object. It's a SQL query builder and browser
for and users.

After installing the module, it adds a menu to define custom report in
the "Dashboard" menu.
""",
	"depends" : ["base"],
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["base_report_creator_wizard.xml","base_report_creator_view.xml"],
	"active": False,
	"installable": True
}
