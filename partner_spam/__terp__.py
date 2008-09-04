{
	"name" : "Partner labels. SMS and Email spam to partner",
	"version" : "1.0",
	"author" : "Zikzakmedia SL",
	"website" : "www.zikzakmedia.com",
	"category" : "Generic Modules",
	"description": """Flexible partner labels:
  * Definition of page sizes, label manufacturers and label formats
  * Flexible label formats (page size, portrait or landscape, manufacturer, rows, columns, width, height, top margin, left margin, ...)
  * Initial data for page sizes and label formats (from Avery and Apli manufacturers)
  * Wizard to print labels. The label format, the printer margins, the font type and size, the first label (row and column) to print on the first page can be set.

Improved SMS and Email spam to partner:
  * Spam to partners and to partner.address (contacts)
  * Choice to spam all partner addresses or partner default addresses
  * The email field can contain several email addresses separated by ,
  * A maximum of 3 files can be attached to emails
  * Clickatell gateway to send SMS can be configured by http or by email
  * The spam text can include special [[field]] tags to create personalized messages (they will be replaced to the the corresponding values of each partner contact):
      [[partner_id]] -> Partner name
      [[name]] -> Contact name
      [[function]] -> Function
      [[title]] -> Title
      [[street]] -> Street
      [[street2]] -> Street 2
      [[zip]] -> Zip code
      [[city]] -> City
      [[state_id]] -> State
      [[country_id]] -> Country
      [[email]] -> Email
      [[phone]] -> Phone
      [[fax]] -> Fax
      [[mobile]] -> Mobile
      [[birthdate]] -> Birthday
	""",
	"depends" : ["base",],
	"init_xml" : ["report_label_data.xml",],
	"demo_xml" : [],
	"update_xml" : ["partner_wizard.xml", "report_label_view.xml",],
	"active": False,
	"installable": True
}
