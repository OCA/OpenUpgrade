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
    "name" : "Partner NACE informations",
    "version" : "0.1",
    "author" : "Sistheo",
    "category" : "Partner NACE informations",
    "description" : """Add NACE informations in categories list.

The Statistical Classification of Economic Activities in the European Community
commonly referred to as NACE, is a European industry standard classification
system consisting of a 6 digit code.

NACE is equivalent to the SIC and NAICS system:

    * Standard Industrial Classification
    * North American Industry Classification System

The first four digits of the code, which is the first four level of the
classification system, are the same in all European countries. The fifth digit
might vary from country to country and further digits are sometimes placed by
suppliers of databases.
    """,
    "depends" : ["base"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "partner_nace_data.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

