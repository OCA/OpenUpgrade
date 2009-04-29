
{
    "name" : "Google Earth/Map Module",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Others",
    "website" : "http://www.openerp.com",
    "depends" : ["base","account"],
    "description": """
            This Module will includes following :

            * Layers with characteristics by regions
            * Display customers, whom country has colors by turnover
            * Most frequent delivery routes
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["google_earth_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: