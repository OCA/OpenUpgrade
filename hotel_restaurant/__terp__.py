{
    "name" : "Hotel Restaurant",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Hotel Restaurant",
    "description": """
    Module for Hotel/Resort/Restaurant management. You can manage:
    * Configure Property
    * Restaurant Configuration
    * table reservation
    * Generate and process Kitchen Order ticket,
    * Payment

    Different reports are also provided, mainly for Restaurant.
    """,
    "depends" : ["base","hotel"],
    "init_xml" : [],
    "demo_xml" : ["hotel_restaurant_data.xml",
    ],
    "update_xml" : [
                    "hotel_restaurant_view.xml",
                    "hotel_restaurant_report.xml",
                    "hotel_restaurant_workflow.xml",
                    "hotel_restaurant_wizard.xml",
                    "hotel_restaurant_sequence.xml",
                    "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}
