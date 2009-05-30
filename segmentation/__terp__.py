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
    "name" : "segmentation management",
    "version" : "1.3",
    "depends" : ["base", 'crm_profiling'],
    "author" : "Tiny",
    "description": """
    This module allow users to create profile and compute automatically which partners do fit the profile criteria. 

    In this version the new concept of questionnaire allow you to regroup questions into a questionnaire and directly use it on a partner.


NOTICE: This Module is Deprecated. Please install crm_profiling in order to have access to the latest functionalities.
    """,
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/Project & Services",
    "init_xml" : [],
    "demo_xml" : ["segmentation_demo.xml"],
    "update_xml" : ["segmentation_view.xml",
            ],
    "active": False,
    "installable": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

