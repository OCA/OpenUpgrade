{
	"name" : "Invoicing Mode",
	"version" : "1.0",
	"depends" : ["hr_timesheet_sheet"],
	"author" : "Tiny",
	"description": """

	This module allows you to define your preferencies for analytic accounts.

	For example, you can say 
	* what is the defaut function of a specific user on a given account, 
	* what is the default invoicing rate for a specific user on a given account,

	This is mostly used when a user encode his timesheet: the values are retrieved and the fields are auto-filled... but the possibility to change these values is still available.

	Obviously if no data has been recorded for the current account, the default values are given as usual so that this module is perfectly compatible with older configurations.

	""",
	"website" : "http://tinyerp.com/",
	"category" : "Generic Modules/Others",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
			"mode_invoicing_view.xml",
			],
	"active": False,
	"installable": True
}
