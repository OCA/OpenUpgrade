# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst, Nicolas bessi
#
#
#    This file is part of the c2c_timesheet_report module
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
    "name" : "Timesheet Reports",
    "version" : "1.1",
    "author" : "camptocamp.com (aw)",
    "category" : "",
    "website" : "http://camptocamp.com",
    "description": """
        Timesheet Reports Module:
            * Add a report "/HR/report/Timesheets/Timesheet Status" that display the timesheet status for each user: "confirmed", "draft", "missing". 
              It displays 5 periods' status previous to a given date
            * Add a field "ended" to the employee form to define when the employee stopped working for the company
            * Add a tool "/HR/Configuration/Timesheet Reminder" to send automatics emails to those who did not complete their timesheet and add a boolean field to employees to define if they should receive this message or not
    """,
    "depends" : ["hr_timesheet_sheet", "hr", "c2c_reporting_tools"],
    "init_xml" : [],
    "update_xml" : [ "c2c_timesheet_view.xml", "c2c_timesheet_report.xml", "c2c_timesheet_wizard.xml" ],
    "active": False,
    "installable": True
}
