# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
    "name" : "Hotel Restaurant",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Hotel Restaurant",
    "description": """
    Module for Hotel/Resort/Restaurant management. You can manage:
    * Configure Property
    * Restaurant Configuration
    * table reservation
    * Generate and process Kitchen Order ticket,
    * Payment

    Different reports are also provided, mainly for Restaurant.
    """,
    "depends" : ["base","hotel"],
    "init_xml" : [],
    "demo_xml" : ["hotel_restaurant_data.xml",
    ],
    "update_xml" : [
                    "hotel_restaurant_view.xml",
                    "hotel_restaurant_report.xml",
                    "hotel_restaurant_workflow.xml",
                    "hotel_restaurant_wizard.xml",
                    "hotel_restaurant_sequence.xml",
                    "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: