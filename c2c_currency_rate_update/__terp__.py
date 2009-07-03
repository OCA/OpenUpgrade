{
	"name" : "Currency Rate Update",
	"version" : "1.0",
	"author" : "Camptocamp SA",
	"website" : "http://camptocamp.com",
	"category" : "Financial Management/Configuration",
	"description": """
Import exchange rates from three different sources on the internet :

1. Admin.ch
   Updated daily, source in CHF. Source type is XML based.


3. European Central Bank !!! TO be ported
   The reference rates are based on the regular daily concertation procedure between
   central banks within and outside the European System of Central Banks,
   which normally takes place at 2.15 p.m. (14:15) ECB time. Source in EUR.
   http://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html

4. Google Finance !!! TO be ported
   Updated daily from Citibank N.A., source in EUR. Information may be delayed.
   This is parsed from an HTML page, so it may be broken at anytime.

5. Yahoo Finance
    Updated daily 

The update can be set under de company form. 
You can set for each services wich currency you want to update
The log of the update are visible under the service note
You can active or deactivate the update
The module uses internal ir_cron feature from OpenERP, so the job is launched once
the server starts if the 'first execute date' is before the current day.
the module support multy company currency in two way :
    the currencies are shared, you can set currency update only on one 
    company
    the currency are separated, you can set currency on every company
    separately
Afunction field let you know your currency configuration    

If in multi-company mode, the base currency will be the first company's currency
found in database.
""",
	"depends" : ["base"],
	"init_xml" : ["security/security.xml"],
	"update_xml" : [
                        "currency_rate_update.xml",
                        "company_view.xml",
                        
                    ],
	"demo_xml" : [],
	"active": False,
	"installable": True
}
