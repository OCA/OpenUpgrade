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

class offer_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(offer_report, self).__init__(cr, uid, name, context)
        self.sum_debit = 0.0
        self.sum_credit = 0.0
        self.localcontext.update({
            'time': time,
#            'offer_steps':self.offer_steps,
            'offer_docs':self.offer_docs,
            'offer_step_docs':self.offer_step_docs,
        })
        self.context = context
    def offer_docs(self,offer_id):
        attachment_ids = self.pool.get('ir.attachment').search(self.cr,self.uid,[('res_id','=',offer_id),('res_model','=','dm.offer')])
#        print attachment_ids
        attachment = self.pool.get('ir.attachment').read(self.cr,self.uid,attachment_ids,['name'])
#        print attachment
        return ','.join(map(lambda x:x['name'],attachment))
    
    def offer_step_docs(self,offer_step_id):
        attachment_ids = self.pool.get('ir.attachment').search(self.cr,self.uid,[('res_id','=',offer_step_id),('res_model','=','dm.offer.step')])
        attachment = self.pool.get('ir.attachment').read(self.cr,self.uid,attachment_ids,['name'])
#        print attachment
        return ','.join(map(lambda x:x['name'],attachment)) 
#    def offer_steps(self,offer_id):
#        offer_step_ids = self.pool.get('dm.offer.step').search(self.cr,self.uid,[('offer_id','=',offer_id)])
#        res = self.pool.get('dm.offer.step').browse(self.cr,self.uid,offer_step_ids)
#        return res
report_sxw.report_sxw('report.offer.report', 'dm.offer', 'addons/dm/report/dm_offer.rml', parser=offer_report)
report_sxw.report_sxw('report.offer.model.report', 'dm.offer', 'addons/dm/report/dm_offer_model.rml', parser=offer_report)
report_sxw.report_sxw('report.preoffer.report', 'dm.offer', 'addons/dm/report/dm_preoffer.rml', parser=offer_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

