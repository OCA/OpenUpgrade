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

import time
from report import report_sxw

class campaign_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(campaign_report, self).__init__(cr, uid, name, context)
        self.sum_debit = 0.0
        self.sum_credit = 0.0
        self.localcontext.update({
            'time': time,
        })
        self.context = context
        
report_sxw.report_sxw('report.dm.campaign.report', 'dm.campaign', 'addons/dm/report/dm_campaign.rml', parser=campaign_report,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

