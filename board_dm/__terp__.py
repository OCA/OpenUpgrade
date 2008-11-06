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
    "name":"Board for DM users",
    "version":"1.0",
    "author":"Tiny",
    "category":"Board/Direct Marketing",
    "depends":[
        "board",
        "dm",
    ],
    "demo_xml":[],
    "update_xml":["board_campaign_manager_view.xml"],
    "description": """
This module implements a dashboard for campaign manager that includes:
    * List of campaigns that have started at max 2 month ago and those that will start in the 2 month to come
    * List of the tasks of the day
    * List of  the tasks with a deadline passed
    """,
    "active":False,
    "installable":True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

