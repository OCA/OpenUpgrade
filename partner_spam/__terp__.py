# -*- encoding: utf-8 -*-
{
    "name" : "SMS and Email spam to partner",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "category" : "Generic Modules",
    "description": """Improved SMS and Email spam to partner:
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
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "partner_wizard.xml",
        "partner_contact_view.xml",
    ],
    "active": False,
    "installable": True
}
