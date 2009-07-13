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
    "name" : "report_analytic_planning_long_term",
    "version" : "1.0",
    "depends" : ["report_analytic_planning"],
    "author" : "Tiny",
    "description": """
This modules is an improvement of the basic planning module and offers additional functionalities for long term planning, such as:
        - planning of the functions that will be needed
        - additional data for planned ressources: the start and end dates
    """,
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/Human Resources",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml":["security/ir.model.access.csv","report_analytic_planning_long_term_view.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

