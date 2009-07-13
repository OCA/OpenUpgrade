# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2008-2009 Syleam Info Services (<http://syleam.fr>). 
#                  All Rights Reserved
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
    "name" : "Telemarketing Management",
    "version" : "1.0",
    "author" : "Syleam",
    "website" : "http://www.syleam.fr",
    "category" : "Generic Modules/CRM & SRM",
    "description": """
Add a new fonctionnality on Questionnaire
New wizard on CRM Case to create a new case
""",
    "depends" : [
        "crm",
        "crm_configuration",
        "crm_profiling",
    ],
    "init_xml" : [
#        "crm_configuration_wizard.xml",
    ],
    "demo_xml" : [],
    "update_xml" : [
        "crm_profiling_wizard.xml",
        "crm_profiling_view.xml",
#         "security/ir.model.access.csv",
#         "process/crm_configuration_process.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

