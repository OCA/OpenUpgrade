{
    "name" : "Reservation Management - Reporting",
    "version" : "1.0",
    "author" : "Tiny",
    "depends" : ["hotel_reservation"],
    "category" : "Generic Modules/Hotel Reservation",
    "description": "A module that adds new reports based on Reservation cases.",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["security/ir.model.access.csv","report_hotel_reservation_view.xml"],
    "active": False,
    "installable": True
}