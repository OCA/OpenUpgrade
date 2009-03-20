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
    "name" : "Dashboard for Service Profile",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Board/Service",
    "description": """
        This module displays three dashboards for the logged in user:
        
        A. Dashboard 1: Weekly Dashboard
                   - Draft Forecasts Lines
                   - Turnover by Product and Month
                   - Aged Receivables
                   - Timesheet to Validate
                   - Sales pipeline
                   - Planning Statistics
                    
                This dashboard is reachable from Dashboards/Service Profile/Weekly Dashboard.
           
        B. Dashboard 2: Daily Dashboard
                   - Open Tasks
                   - Pending Tasks
                   - Inbox
                   - Meeting of the Day
                   - Departement's Timesheet Lines of last 3 days.
        
                This dashboard is reachable from Dashboards/Service Profile/Daily Dashboard.
                
        C. Dashboard 3 : Random Activities
                   - Random Timesheet Lines from the past 15 days
                   - Random Tasks Closed within the past 15 days
                   - Random Cases Closed within the past 15 days
                   - Random Open Cases Created within the past 15 days
                   - Random Sales Orders Created within the past 15 days
                   - Random Invoices Created within the past 15 days 

                This dashboard is reachable from Dashboards/Service Profile/Random Activities(Within Last 15 Days).
                
                """,
    "depends" : ["base",
                 "project_gtd",
                 "board_project",
                 "sale_forecast",
                 "crm_configuration",
                 "report_account",
                 "report_analytic_planning",
                 "report_sale",
                 "report_crm",
                 "report_task",
                 "report_timesheet",
                 ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "board_service_view.xml",
                    ],
    "active": False,
    "installable": True,    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

