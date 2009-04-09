# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst
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

from osv import fields, osv
import time
import pooler


class c2c_budget_report_abstraction(osv.osv):
    """ This object define parts of reports that can be override. 
        It is used to replace analytic_account by projects for some of ours customers """
    
    _name = "c2c_budget.report_abstraction"
    _description = "Report Abstraction"
    _columns = {}
    _defaults = {}
        
        
    def get_project_group_object(self, cr, uid, context={}):
        """ return the object use to group by projects in reports 
            this is an abstraction level use to allow this module to be overridden in order to use project as analytic accounts
        """
        return self.pool.get('account.analytic.account');
        
        
    
c2c_budget_report_abstraction()