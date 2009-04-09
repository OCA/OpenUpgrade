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
    "name" : "Asterisk",
    "version" : "0.1proto2",
    "author" : "Tiny",
    "category" : "Enterprise Specific Modules/Electronic Industries",
    "depends" : ["base"],
    "init_xml" : [],
    "demo_xml" : ["asterisk_demo.xml"],
    "description": """Manages a list of asterisk servers and IP phones.
This module implements a system to popup the partner form based on phone calls.
This is still a proof of concept, that have been made during Tiny ERP's
technical training session.""",
    "update_xml" : ["security/ir.model.access.csv","asterisk_view.xml","asterisk_wizard.xml"],
    "active": False,
    "installable": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

