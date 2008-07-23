# -*- encoding: utf-8 -*-
{
    "name" : "Human Resources Timesheets on contracts",
    "version" : "0.1",
    "author" : "Tiny",
    "category" : "Generic Modules/Human Resources",
    "website" : "http://tinyerp.com/module_hr.html",
    "depends" : ["hr_contract","hr_timesheet"],
    "module": "",
    "description": """
        Compute the cost of an employee for his timesheets according
        to his contract definitions. If no contract are defined, it
        uses the product costs linked to the employee.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

