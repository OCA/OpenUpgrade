#
#       On Demand Management System Module
# 
{
        "name" : "Module for the On Demand Management System",
        "version" : "1.0",
        "author" : "Tiny",
        "category" : "Generic Modules/Others",
        "website": "http://www.tinyerp.com",
        "description": "Module to manage the Tiny On Demand Management System",
        "depends" : ["base","base_vat","sale","crm","portal"],
        "init_xml" : ["odms_data.xml"],
        "update_xml" : ["odms_wizard.xml", "odms_view.xml","odms_sequence.xml", "odms_portal.xml", "odms_portal_security.xml"],
        "active": False,
        "installable": True
}
