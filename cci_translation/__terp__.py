# -*- encoding: utf-8 -*-
{
    "name" : "CCI Translation",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Translation",
    "description": """
        cci translation
    """,
    "depends" : ["base","cci_account"],
    "init_xml" : [],
    "demo_xml" : ["cci_translation_data.xml"],

    "update_xml" : ["cci_translation_view.xml", "cci_translation_workflow.xml", "cci_translation_wizard.xml"
                    ,"cci_translation_sequence.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

