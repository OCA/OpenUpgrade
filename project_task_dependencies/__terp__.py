# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) P. Christeas, 2009
# all rights reserved
# created 2008-07-05
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
	"name" : "Task Dependencies",
	"version" : "0.2",
	"author"  : "ChriCar Beteiligungs und Beratungs GmbH, P. Christeas" ,
	"website" : "http://www.chricar.at/ChriCar",
        "description"  : """This module adds dependencies between tasks 
         and recalculates the sequence numbers, which are used 
         * to print the Gantt graph
         * to order the tasks
	 """,
	"category" : "Generic Modules/Others",
	"depends" : ["base","project"],
	"init_xml" : [],
	"demo_xml" : ["task_dependencies_demo.xml"],
	"update_xml" : ["task_dependencies_view.xml"],
	"active": False,
	"installable": True
}
