# -*- encoding: utf-8 -*-
{
    "name" : "Hotel Housekeeping",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Hotel Housekeeping",
    "description": """
    Module for Hotel/Hotel Housekeeping. You can manage:
    * Housekeeping process
    * Housekeeping history room wise

      Different reports are also provided, mainly for hotel statistics.
    """,
    "depends" : ["hotel"],
    "init_xml" : [],
    "demo_xml" : [
    ],
    "update_xml" : ["hotel_housekeeping_view.xml",
                    "hotel_housekeeping_workflow.xml",
                    
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

