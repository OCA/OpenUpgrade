# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_report_tools module.
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
{
	"name" : "c2c Reporting Tools. A library that provide a new way to create clean reports efficiently",
	"version" : "5.0",
	"author" : "Camptocamp",
	"category" : "Generic Modules/Reporting",
	
	
	"description": """  This module offer a growing collection of objects to create simple and advanced reports in a new way of doing.
	               You can create powerful reports with a few lines of python code and nothing else. (no sxw, rml or xml)
				   This module follow multiple goals: 
				     - To accelerate report creation by creating reusable pieces of code (one line of code to create standard header and footer)
				     - To accelerate report generation (processing) by getting ride of uncecessary parsing and transformations (direct python to pdf generation) 
				     - To improve reporting capabilities by getting ride of uncomplete parsers and limited middle technologies 
				     - To make reports designs more uniform 
				   
				   For exemples of use, have a look at c2c_planning_management. Our first module based on this tool.
				   
			  """,
	
	"website": "http://www.camptocamp.com",
	"depends" : [],
	"init_xml" : [
		],
	"update_xml" : [
	],
	"active": False,
	"installable": True
}


