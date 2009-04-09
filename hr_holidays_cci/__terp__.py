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
    "name" : "Human Resources: Holidays management",
    "version" : "0.1",
    "author" : "Axelor",
    "category" : "Generic Modules/Human Resources",
    "website" : "http://www.axelor.com/",
    "description": """Human Ressources: Holidays summary printing functionality 


NOTICE: This Module is Deprecated. Please install hr_holidays in order to have latest functionalities.""",
    "depends" : ["hr_holidays",],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["hr_view.xml","hr_holidays_report.xml","hr_holidays_wizard.xml",],
    "active": False,
    "installable": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

