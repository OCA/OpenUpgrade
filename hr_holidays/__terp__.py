{
	"name" : "Human Resources: Holidays management",
	"version" : "0.1",
	"author" : "Tiny & Axelor",
	"category" : "Generic Modules/Human Resources",
	"website" : "http://tinyerp.com/",
	"description": """Human Ressources: Holidays tracking and workflow

	Note that:
	- You can set up your color preferencies in
				HR \ Configuration \ Holidays Status
	- There are two ways to print the employee's holidays:
		* The first will allow to choose employees by department and is used by clicking the menu item located in
				HR \ Holidays Request \ Print Summary of Holidays
		* The second will allow you to choose the holidays report for specific employees. Go on the list
				HR \ Employees \ Employees
			then select the ones you want to choose, click on the print icon and select the option
				'Print Summary of Employee's Holidays'
	- The wizard allows you to choose if you want to print either the Confirmed & Validated holidays or only the Validated ones. These states must be set up by a user from the group 'HR' and with the role 'holidays'. You can define these features in the security tab from the user data in
				Administration \ Users \ Users
			for example, you maybe will do it for the user 'admin'.
""",
	"depends" : ["hr","crm"],
	"init_xml" : [],
	"demo_xml" : ["hr_bel_holidays_2008.xml",],
	"update_xml" : ["hr_workflow.xml","hr_view.xml","hr_holidays_report.xml","hr_holidays_wizard.xml",],
	"active": False,
	"installable": True
}
