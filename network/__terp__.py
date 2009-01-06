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
    "name" : "Network Management",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Enterprise Specific Modules/Information Technology",
    "depends" : ["base"],
    "init_xml" : [],
    "description": """
    A simple module to encode your networks and materials:
    - networks and connections between networks
    - hardwares and softwares with:
        - versions, access rights, waranties

    You can print interventions form for technical people.""",
    "demo_xml" : ["network_demo.xml"],
    "update_xml" : ["security/ir.model.access.csv", "network_view.xml", "network_report.xml"],
    "active" : False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

