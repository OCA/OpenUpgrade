# -*- encoding: utf-8 -*-
{
    "name" : "segmentation management",
    "version" : "1.3",
    "depends" : ["base", 'crm_profiling'],
    "author" : "Tiny",
    "description": """
    This module allow users to create profile and compute automatically which partners do fit the profile criteria. 

    In this version the new concept of questionnaire allow you to regroup questions into a questionnaire and directly use it on a partner.


NOTICE: This Module is Deprecated. Please install crm_profiling in order to have access to the latest functionnalities.
    """,
    "website" : "http://tinyerp.com/",
    "category" : "Generic Modules/Project & Services",
    "init_xml" : [],
    "demo_xml" : ["segmentation_demo.xml"],
    "update_xml" : ["segmentation_view.xml",
            ],
    "active": False,
    "installable": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

