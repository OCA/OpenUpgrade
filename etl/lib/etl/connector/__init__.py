# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
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

"""

 Use to provide connection with any resources like localfile, database, openerp server etc..

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
GNU General Public License
"""
from connector import connector
from localfile import localfile
from sql_connector import sql_connector
from openobject_connector import openobject_connector
from facebook_connector import facebook_connector
from sugarcrm_connector import sugarcrm_connector
from xmlrpc_connector import xmlrpc_connector
