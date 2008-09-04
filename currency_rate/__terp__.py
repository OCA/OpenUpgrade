{
    "name" : "Currency Rates",
    "version" : "1.0",
    "author" : "Axelor",
    "category" : "Generic Modules",
    "website": "http://www.axelor.com",
    "depends" : ["base", "multi_company_currency"],
    "init_xml" : [],
    "update_xml" : [
                    "currency_data.xml",
                    "currency_wizard.xml",                                     
                    ],
    "demo_xml" : [],
    "installable": True,
    "active" : False,
}
