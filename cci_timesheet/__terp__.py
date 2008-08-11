# -*- encoding: utf-8 -*-
{
    "name" : "CCI Timesheet",
    "version" : "1.0",
    "author" : "OpenERP",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/CCI Timesheet",
    "description": """
        A Customized timesheet module.
    """,
    "depends" : ["base","cci_partner","cci_crm","cci_base_contact"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["cci_timesheet_view.xml", "cci_timesheet_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

