# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "SMS and Email spam to partner",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "license" : "GPL-3",
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
    "depends" : ["base","smtpclient"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "partner_wizard.xml",
        "partner_contact_view.xml",
    ],
    "active": False,
    "installable": True
}
