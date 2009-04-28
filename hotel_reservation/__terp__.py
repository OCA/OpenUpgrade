{
    "name" : "Hotel Reservation",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Hotel Reservation",
    "description": """
    Module for Hotel/Resort/Property management. You can manage:
    * Guest Reservation
    * Group Reservartion
      Different reports are also provided, mainly for hotel statistics.
    """,
    "depends" : ["hotel"],
    "init_xml" : [],
    "demo_xml" : ['hotel_reservation_data.xml',
    ],
    "update_xml" : [
                    "hotel_reservation_view.xml",
                    "hotel_reservation_sequence.xml",
                    "hotel_reservation_workflow.xml",
                    "hotel_reservation_wizard.xml",
                    "hotel_reservation_report.xml",
                    "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}