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
    "name" : "Accounting journal visibility",
    "version" : "1.0",
    "depends" : ["account"],
    "author" : "Tiny",
    "category" : "Generic Modules/Accounting",
    "description": """
    Using this module :
    when we open the journals list, people will only see journal for which they are allowed
    (means their group is specified on the journal definition). and also
    Only people in the group defined on the journal will be able to see the invoices of this journal.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["account_journal_view.xml"],
    "active": False,
    "installable": True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

