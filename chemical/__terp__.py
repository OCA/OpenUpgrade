# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
#
# Use the custom module to put your specific code in a separate module.
#
{
	"name" : "Module for Chemical Industries",
	"version" : "1.0",
	"author" : "H&D",
	"category" : "Enterprise Specific Modules/Chemical Industries",
	"website": "http://www.hu-div.fr",
	"depends" : ["base", "account", "product", "stock"],
	"init_xml" : [],
	"description":"Module for Chemical Industries",
	"update_xml" : ['security/ir.model.access.csv',
		"product/risque_securite_danger.xml",
		"product/product_view_chem.xml",
			],
	"active": False,
	"installable": True,
	"certificate": '009574510892061',
}

