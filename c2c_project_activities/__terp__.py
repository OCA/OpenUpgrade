# -*- coding: utf-8 -*-
##############################################################################
#
# @author Grand-Guillaume Joel, ported by Nicolas Bessi to 5.0
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
	"name" : "Project activities",
	"version" : "1.0",
	"author" : "Camptocamp",
	"category" : "Generic Modules/Human Resources",
	"module":
"""
    Add activities on analytic account which can be choosen in timesheet completion. The goal is to improve 
    statistics on wich activities take time in project. Users will choose for each timesheet line a related activity.
    Adding activities on parent account will allow child to benefit from. So you can define a set of activities 
    for each parent analytic account like:

	Administratif
		- Intern
		- Project 1
	Customers project
		- Project X
		- Project Y
	What will be true for Administratif, will be true for Intern too.
""",
	"website": "http://camptocamp.com",
	"depends" : ["account",
                "hr_timesheet_sheet",
                "project"
                ],
	"init_xml" : ["security/c2c_project_activites_security.xml"],
	"demo_xml" : ["c2c_activities_demo.xml"],
	"update_xml" : [
		"c2c_project_activities_view.xml",
	],
	"active": False,
	"installable": True
}
