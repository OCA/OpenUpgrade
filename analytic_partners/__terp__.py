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
    "name" : "Analytic accounts with multiple partners",
    "author" : "Tiny",
    "version" : "1.0",
    "category" : "Generic Modules/Others",
    "depends" : ["account"],
    "description": """
    This module adds the possibility to assign multiple partners on
    the same analytic account. It's usefull when you do a management
    by affairs, where you can attach all suppliers and customers to
    a project.

    A report for the project manager is added to print the analytic
    account and all associated partners with their contacts.

    It's usefull to give to all members of a project, so that they
    get the contacts of all suppliers in this project.
    """,
    "demo_xml" : [],
    "update_xml" : ["analytic_partners_view.xml",
                        "analytic_partners_report.xml"],
    "init_xml" : [],
    "active": False,
    "installable": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

