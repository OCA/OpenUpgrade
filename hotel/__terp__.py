# -*- encoding: utf-8 -*-
{
    "name" : "Hotel Management",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Hotel Management",
    "description": """
    Module for Hotel/Resort/Property management. You can manage:
    * Configure Property
    * Hotel Configuration
    * Check In, Check out
    * Manage Folio
    * Payment

    Different reports are also provided, mainly for hotel statistics.
    """,
    "depends" : ["base","product","sale"],
    "init_xml" : [],
    "demo_xml" : ["hotel_data.xml",
    ],
    "update_xml" : ['hotel_view.xml',
                    "hotel_folio_workflow.xml",
                    "hotel_report.xml",
                    "hotel_wizard.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

