#!/usr/bin/env python
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
	"name" : "City for base_contact",
	"version" : "1.0",
	"author" : "Pablo Rocandio",
	"category" : "Generic Modules/Base",
	"description": """Zip code, city, state and country fields are replaced with a location field in partner form when base_contact module is installed.
This module helps to keep homogeneous address data in our database.
You should use this module if you are already using base_contact and city""",
	"depends" : ["base", "base_contact", "city"],
	"init_xml" : [],
	"update_xml" : [
	    'city_view.xml',
	    ],
	"active": False,
	"installable": True
}
