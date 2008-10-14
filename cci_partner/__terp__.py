# -*- encoding: utf-8 -*-
{
    "name" : "CCI Partner",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Partner",
    "description": """
        Specific module for cci project which will inherit partner module
    """,
    "depends" : ["base","base_vat","cci_base_contact","account_l10nbe_domiciliation","cci_country"],
    "init_xml" : [],
    "demo_xml" : [ "cci_data.xml", 
#"user_data.xml",
"zip_data.xml", "courtesy_data.xml","links_data.xml", 
"activity_data.xml", 
#"states_data.xml", 
#"category_data.xml", 
"function_data.xml"],

    "update_xml" : ['cci_partner_view.xml','article_sequence.xml','cci_partner_report.xml','cci_partner_wizard.xml'],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

