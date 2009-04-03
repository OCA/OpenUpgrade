# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution····
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
import time
import datetime
import warnings
import netsvc
from mx import DateTime

from osv import fields
from osv import osv


class dm_customers_file(osv.osv):
    _inherit = "dm.customers_file"

    _columns = {
                'case_ids' : fields.many2many('crm.case','crm_case_customer_file_rel','lead_id','cust_file_id','CRM Leads')
            }

dm_customers_file()

class dm_workitem(osv.osv):
    _inherit = "dm.workitem"

    _columns = {
                'case_id' : fields.many2one('crm.case','CRM Leads')
            }

dm_workitem()

