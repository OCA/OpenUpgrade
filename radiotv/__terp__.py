# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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
    "name" : "Tiny ERP TV & Radio Program Grid Module",
    "version" : "1.1",
    "author" : "Zikzakmedia",
    "website": "www.zikzakmedia.com",
    "license" : "GPL-3",
    "category" : "Generic Modules/Others",
    "description" : """This module allows to control TV & Radio channels, programs, grid of date/time of broadcasting and podcasts

channel <--n---m--> program <--1---n--> broadcast <--1---n--> podcast

Features:
    * Menu entries to see daily and weekly broadcasts
    * The date/time end of each broadcast is computed automatically
    * The broadcasts can be copied from a range of days to other
    * A TinyERP cron is provided to copy broadcasts every day
    * Several broadcasting reports are included
    * Several wizards to synchronize the channels, programs and broadcasts to a
      mysql-php web site are included. They can be also synchronized automatically.""",
    "depends" : ["base"],
    "init_xml" : ['radiotv_data.xml',],
    "demo_xml" : [],
    "update_xml" : [
        "security/radiotv_security.xml",
        "security/ir.model.access.csv",
        'radiotv_view.xml',
        'radiotv_report.xml',
        'radiotv_wizard.xml',
    ],
    "installable" : True,
    "active" : False,

}