
{
    "name" : "Google Earth/Map Module",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Others",
    "website" : "http://www.openerp.com",
    "depends" : ["sale"],
    "description": """
            This Module will includes following :

            * Layers with characteristics by regions (menu: Partners/Google Map/Earth)
            * Display customers, whom country has colors by turnover (menu: Partners/Google Map/Earth)
            * Most frequent delivery routes (menu: on stock.picking)

    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["google_earth_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: