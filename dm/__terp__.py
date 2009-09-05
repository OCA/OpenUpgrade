# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
    "name" : "Direct Marketing",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/Direct Marketing",
    "description": """

        Marketing Campaign Management Module

        This module allows to :

        * Commercial Offers :
            - Create  Multimedia Commercial Offers
            - View a Graphicalreprsesentation of the offer steps
            - Create offers from offer models and offer ideas

        * Marketing Campaign
            - Plan your Marketing Campaign and Commercial Propositions
            - Generate the Retro planning (automaticaly creates all the tasks necessary to launch your campaign)
            - Assign automatic prices to the items of your commercial propositions
            - Auto generate the purchase orders for all the items of the campaign
            - Manage Customers Fils, segments and segmentation criteria
            - Create campaigns from campaign models
            - Manage copywriters, brokers, dealers, addresses deduplicators and cleaners

            """,
    "depends" : [
                 "base_language","document","base_report_designer",
                 "sale","base_partner_gender", "crm", "smtpclient",
                ],
    "init_xml" : [
                 ],
    "demo_xml" : [
                    "dm_demo.xml",
                 ],
    "update_xml" : [
                    "security/dm_security.xml",
                    "security/ir.model.access.csv",
                    "dm_wizard.xml",
                    "dm_campaign_view.xml",
                    "dm_offer_view.xml",
                    "dm_offer_step_view.xml",
                    "dm_customer_view.xml",
                    "dm_engine_view.xml",
                    "dm_inherit_view.xml",
                    "dm_report.xml",
                    "dm_offer_sequence.xml",
                    "dm_data.xml",
                    "dm_workflow.xml",
                    "dm_document_view.xml",
                    ],
    "active": False,
    "installable": True,
#    'certificate': '0176807797184'    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

