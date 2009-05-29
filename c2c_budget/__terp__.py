# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst ported by nbessi
# 
#    This file is part of the c2c_budget module
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
    "name" : "Advanced Budget",
    "version" : "5.0",
    "author" : "Camptocamp SA (aw)",
    "category" : "Generic Modules/Accounting",
    "website" : "http://camptocamp.com",
    "description": """
    Budget Module:
    * Create budget, budget items and budget versions.
    * Base your budget on analytics accounts
    * Budget versions are multi currencies and multi companies.

    This module is for real advanced budget use, otherwise prefer to use the Tiny one.
    """,
    "depends" : [
                    "base",
                    "account",
                    "c2c_reporting_tools"
                ],
    "init_xml" : [],
    "update_xml" : [
                        "c2c_budget_view.xml",
                        "c2c_budget_wizard.xml",
                        "security/ir.model.access.csv"
                    ],
    "active": False,
    "installable": True
}
