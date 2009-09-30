#########################################################################
# Copyright (C) 2009  Sharoon Thomas  & Open ERP Community              #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

{
    "name" : "Product - Many Categories",
    "version" : "1.0.2",
    "author" : "Sharoon Thomas",
    "website" : "",
    "category" : "Added functionality",
    "depends" : ['base','product'],
    "description": """
    This module Extends the existing functionality of Open ERP Products (One product - One Catgory)
    to One product -> Many Categories

    *Note: This module was built generically but in focus of the Magento Open ERP connector
    """,
    "init_xml": [],
    "update_xml": [
            'product_view.xml'
    ],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
