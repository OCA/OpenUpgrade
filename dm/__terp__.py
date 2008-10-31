# -*- encoding: utf-8 -*-
{
    "name" : "Direct Marketing",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/Direct Marketing",
    "description": """

        Marketing Campaign Management Module

        This module allows to manage :

        * Commercial Offers :
            - Create Commercial Offers
            - Multimedia aware
            - Graphical View of the Offer Steps
            - Create offers from offer models
            - Preoffer management (ideas)

        * Marketing Campaign
            - Marketing Campaign Plannification
            - Retro planning generation (automaticaly creates all the tasks necessary to launch your campaign)
            - Assign automatic price progression for each campaign steps
            - Auto generate the pruchase orders for all the products of the campaign
            - Manage Customers segments and segmentation criteria
            - Create campaigns from campaign models
            - Manage copywriters, brokers, dealers, addresses deduplicators and cleaners

            """,
    "depends" : ["project_retro_planning","purchase","board"],
    "init_xml" : [ ],
    "demo_xml" : [
                  "campaign_data.xml",
                  ],
    "update_xml" : [
                    "dm_wizard.xml",
                    "dm_security.xml",
                    "offer_view.xml",
                    "offer_step_view.xml",
                    "trademark_view.xml",
                    "campaign_view.xml",
                    "dm_report.xml",
                    "offer_sequence.xml",
                    "dm_data.xml",
#                    "board_campaign_manager.xml",
                    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

