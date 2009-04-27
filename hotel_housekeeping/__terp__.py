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
    "demo_xml" : ["hotel_housekeeping_data.xml",
    ],
    "update_xml" : [
                    "hotel_housekeeping_view.xml",
                    "hotel_housekeeping_workflow.xml",
                    "hotel_housekeeping_report.xml",
                    "hotel_housekeeping_wizard.xml",
                    "security/ir.model.access.csv",


    ],
    "active": False,
    "installable": True
}