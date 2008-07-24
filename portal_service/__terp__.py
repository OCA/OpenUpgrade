# -*- encoding: utf-8 -*-
{
    "name" : "Portal Management - Service",
    "version" : "0.1",
    "author" : "Tiny",
    "website" : "http://tinyerp.com/",
    "depends" : ["base", "portal","project","crm",
                 "account_analytic_analysis","hr_timesheet_invoice",
                 "scrum",],
    "category" : "Generic Modules/Others",
    "description": "Potal Management - Service company specific data.",
    "init_xml" : [],
    "update_xml" : ["portal_project_view.xml","portal_project_data.xml",
                    "portal_crm_view.xml","portal_crm_data.xml",
                    "portal_scrum_view.xml","portal_scrum_data.xml",
                    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

