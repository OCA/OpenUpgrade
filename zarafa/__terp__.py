{
    "name" : "Zarafa Integration",
    "version" : "1.0",
    "author" : "Sednacom",
    "category" : "Generic Modules/Others",
    "website": "http://www.sednacom.fr",
    "description": "New objetcs and views to improve use of OpenERP:\n * shortcuts view\n * module view\n * email object\n * Zarafa tools",
    "depends" : ["base","crm",],
    "init_xml" : [],
    "update_xml" : [
        "sednacom_view.xml" ,
        "sednazarafa_view.xml" ,
        "email_view.xml",
        ],
    "active": False,
    "installable": True
}
