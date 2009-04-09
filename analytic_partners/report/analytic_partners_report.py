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
import pooler
import time
from report import report_sxw

class analytic_partners_report(report_sxw.rml_parse):
    # o must be an instance of
    # analytic_partners_account_analytic_account.
    def _init_dict(self, o):
        self.partners_by_account.clear()
        for a in o.address_ids:
            p = a.partner_id
            for c in p.category_id:
                self.partners_by_account.setdefault(c.name, []).append(a)
            if not p.category_id:
                self.partners_by_account.setdefault('Non classifie', []).append(a)


    def __init__(self, cr, uid, name, context):
        # self.partners_by_account is a dictionnary where keys are category
        # names and values are lists of partner_id.
        self.partners_by_account={}
        super(analytic_partners_report, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time' : time,
            '_init_dict' : self._init_dict,
            'partners_by_account' : self.partners_by_account,
        } )

report_sxw.report_sxw(
    'report.analytic_partners.print',
    'account.analytic.account',
    'addons/analytic_partners/report/analytic_account_partners.rml',
    parser=analytic_partners_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

