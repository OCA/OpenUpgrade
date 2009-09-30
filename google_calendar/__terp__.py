{
    "name" : "Google calendar",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules",
    "description": """
        Export events (crm) to google calendar
    """,
    "depends" : ["base", "event"],
    "init_xml" : [],
    "demo_xml" : ['google_calendar_demo.xml'],
    "update_xml" : ['google_calendar_view.xml', 'google_calendar_wizard.xml'],
    "active": False,
    "installable": True,
}