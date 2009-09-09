# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (c) 2008 Acysos SL. All Rights Reserved.
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
	"name" : "Account Move Reverse",
	"version" : "1.0",
	"author" : "ACYSOS S.L.",
	"description" : """ This module adds a wizard to help reversing moves. This can be used to correct mistakes where it's not possible to cancel moves or even for creating close/open moves for periods or fiscalyears. """,
	"license" : "GPL-3",
	"category" : "Generic Modules/Accounting",
	"depends" : ["account"],
	"demo_xml" : [],
	"update_xml" : [
		"account_wizard.xml"
	],
	"active": False,
	"installable": True,

}
