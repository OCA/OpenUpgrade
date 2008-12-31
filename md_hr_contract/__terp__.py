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
    "name" : "Pilot Human Resource Management",
    "version" : "1.0",
    "author" : "Tiny",
    "depends" : ["base","hr","hr_contract"],
    "description": """
    Contract Module for human resource management. You can manage:
    * Contract of the employee
    * Availability of the employee
    and many more.................
    """,
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["security/ir.model.access.csv","md_hr_contract_view.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

