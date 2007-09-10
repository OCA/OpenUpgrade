#
# Use the custom module to put your specific code in a separate module.
# 
{
	"name" : "Switzerland localisation",
	"version" : "1.0",
	"author" : "Camptocamp",
	"category" : "Localisation/Europe",
	"website": "http://www.tinyerp.com",
	"depends" : ["base", "account", "base_vat", "base_iban","account_payment"],
	"init_xml" : ["dta_data.xml", "vaudtax_data.xml", "zip_code_default.xml",],
	"demo_xml" : ["vaudtax_data_demo.xml","dta_demo.xml"],
	"update_xml" : [
		"dta_view.xml","dta_wizard.xml",
		"v11_wizard.xml","v11_view.xml",
		"account_vat.xml","base_config.xml","account_config.xml",
		"bvr_report.xml",
		"bvr_wizard.xml",
		"company_view.xml",
	],
	"active": False,
	"installable": True,
}
