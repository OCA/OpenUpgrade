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
    "name" : "CCI mission",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/CCI",
    "description": """
        specific module for cci project.
    """,
    "depends" : ["base","crm","cci_partner","product","membership", "sale","cci_event","cci_account","cci_translation","cci_country"],
    "init_xml" : [],
    "demo_xml" : ["cci_mission_data.xml"],
    "update_xml" : ["cci_mission_view.xml","cci_mission_wizard.xml","cci_mission_report.xml","cci_mission_workflow.xml",'security/security.xml','security/cci_missions_security.xml','security/ir.model.access.csv'],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

