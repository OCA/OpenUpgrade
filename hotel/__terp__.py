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
    "demo_xml" : [
    ],
    "update_xml" : [

                    "hotel_view.xml",
                    "hotel_data.xml",
                    "hotel_folio_workflow.xml",
                    "hotel_report.xml",
                    "hotel_wizard.xml",
                    "security/hotel_security.xml",
                    "security/ir.model.access.csv",

    ],
    "active": False,
    "installable": True
}