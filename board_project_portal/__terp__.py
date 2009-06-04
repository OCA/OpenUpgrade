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


{
    'name': 'Board for project users',
    'version': '1.0',
    'category': 'Board/Project_Portal',
    'description': """
This module implements a dashboard for project member that includes:
    * List of my open tasks
    * List of my Bugs
    * List of Features
    * List of Supported Requests
    * List of Supported Documents
    * Shortcut Buttons
    * Graph of my work analysis
    * Graph of Bugs status
    """,
    'author': 'Tiny',
    'depends': [
        'project',
        'report_timesheet',
        'board',
        'report_analytic_planning',
        'report_analytic_line',
        'report_task',
        'hr_timesheet_sheet',
        'portal_project',
        'base',
        'crm_configuration',
    ],
    'update_xml': ['board_portal_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
