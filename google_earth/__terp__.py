
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
                - country wise turnover display (low turnover=light red, high turnover=dark red) with information
                - partners display on map with its information
            * Display customers, whom country has colors by turnover (menu: Partners/Google Map/Earth)
                - partners display on map with its turnover
            * Most frequent delivery routes (menu: Partners/Google Map/Earth)
                - grouping of delivery by city and put route path on map with differnt color by number of deliveries
            * Network link kml file for dynamic updates of data on google earth.
            * directly open google map in your browser with different information.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["google_earth_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: