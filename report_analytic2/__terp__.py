{
	"name" : "report_analytic",
	"description": """Reporting for data related to analytic accounts""",
	"version" : "1.0",
	"author" : "OpenErp",
	"category" : "Generic Modules/Analytic Accounting",
	"module": "",
	"website": "http://www.openerp.com/",
	"depends" : ["account","hr_timesheet","hr_timesheet_invoice"],
	"init_xml" : [],
	"update_xml" : [
		"account_analytic_analysis_view.xml",
	],
	"demo_xml" : [],
	"active": False,
	"installable": True
}
